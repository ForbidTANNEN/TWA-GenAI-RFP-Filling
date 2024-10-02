//Main javascript file

import { session } from './jsModules/sessionManager.js';
import { exportFile } from './jsModules/exportFile.js';
import { saveToDB, updateContext, trashcanClick } from './jsModules/pineconeUtils/pineconeButtons.js';
import { getAnswerFromQuestions, fillOutQuestionAnswers } from './jsModules/retrieveLLMAnswer.js';
import { sendFile } from './jsModules/uploadInitialization.js'

//Initialization of the DOM being loaded
document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('llmInstructionTextArea').textContent = session.mainLLMInstructions;
    
    const qaContainer = document.querySelector('.QA'); 
    qaContainer.addEventListener('click', function(event) {

        const clickedElement = event.target.closest('.qa-pair');
        if (clickedElement) {

            document.querySelectorAll('.qa-pair p').forEach(p => {
                p.classList.remove('highlighted');
            });

            session.highlightedQuestionId = clickedElement.id;

            const paragraphs = clickedElement.querySelectorAll('p');
            paragraphs.forEach(p => p.classList.add('highlighted'));

            refreshDOMToClicked();
        }
    });

    //connecting html buttons to functions

    document.getElementById('uploadButton').addEventListener('click', sendFile);

    document.getElementById('exportButton').addEventListener('click', exportFile);

    document.getElementById('alteredQuerySubmit').addEventListener('click', promptChange);

    document.getElementById('uploadDBButton').addEventListener('click', saveToDB);

    document.getElementById('alteredResponseSubmit').addEventListener('click', alteredResponseSubmit);

});

//Correctly resizes page as window is resized or zoomed in/out
$(window).resize(function() {
    resetQAHeight();
});
window.addEventListener("resize", resetQAHeight)

//Sets the question and answer pairs html borders to be equal heights
export function resetQAHeight() {
    session.qaList.forEach((item, index) => {
        const answer = $(`.qa-pair#${index+1} .answer`);
        const question = $(`.qa-pair#${index+1} .question`);
        answer.css('height', '');
        question.css('height', '');
        const answerHeight = answer.height();
        const questionHeight = question.height();
        if (questionHeight > answerHeight) {
            answer.css('height', questionHeight + 'px'); 
        } else {
            question.css('height', answerHeight + 'px');
        }
    });
}

//Formats html text-areas to auto-resize as they are filled with text
$(".text-fixed-size").each(function () {
    this.setAttribute("style", "height:" + (this.scrollHeight));
}).on("input", function () {
    this.style.height = 0;
    this.style.height = (this.scrollHeight) + "px";
});

//Repopulates the "answerInfo" and DOM with the information about the currently clicked QA pair
function refreshDOMToClicked(){

    console.log(session.qaList);

    const selectedQA = session.qaList.find(item => item.id == session.highlightedQuestionId);
        
    document.getElementById('alteredQuery').value = selectedQA.augmentedPrompt;
    $("#alteredQuery").trigger('input');

    document.getElementById('alteredResponse').value = selectedQA.answer;
    $("#alteredResponse").trigger('input');

    fillInContext(selectedQA.context);
}

//Saves the answer in the "alteredResponse" textarea to DOM and current export
function alteredResponseSubmit(){

    const alteredQuery = document.getElementById('alteredResponse').value;
    
    const selectedQA = session.qaList.find(item => item.id == session.highlightedQuestionId);
    selectedQA.answer = alteredQuery;

    const highlightedPair = document.getElementById(session.highlightedQuestionId);

    const answerPara = highlightedPair.querySelector('.answer p');

    answerPara.textContent = alteredQuery;
    resetQAHeight();
};

//Retrieves a new llm answer from the currently entered prompt - then refreshes DOM
export async function promptChange(){

    document.getElementById('loadingScreen').style.display = 'block'; 
    const newPrompt = document.getElementById('alteredQuery').value;

    getAnswerFromQuestions([newPrompt])
        .then(answer => {

            let newAnswer = answer[0]['answer'];
            let newContext = answer[0]['context'];
            let selectedQA = session.qaList.find(item => item.id == session.highlightedQuestionId);

            selectedQA.augmentedPrompt = newPrompt;
            selectedQA.context = newContext;

            if (newAnswer == "I don't know.") {
                selectedQA.answerIsIDK = true;
            }        

            refreshDOMToClicked();
            document.getElementById('alteredResponse').value = newAnswer;
            $("#alteredResponse").trigger('input');

            fillInContext(selectedQA.context);
            resetQAHeight();
            document.getElementById('loadingScreen').style.display = 'none';
        })
        .catch(error => {
            console.error('Failed to get answer for:', newPrompt, 'Error:', error);
        });
}

//Takes in context dictionairy and fills in answer info's "sources referenced" collumn
function fillInContext(context){

    const contextsDiv = document.querySelector('.contexts');
    contextsDiv.innerHTML = '';

    context.forEach((contextInfo, index) => {
        let context_text = contextInfo.text.replace(/\\/g, '');
        let context_title = contextInfo.title
        let context_id = contextInfo.id;
    
        // Create textarea element
        const textarea = document.createElement('textarea');
        textarea.className = 'contextText form-control text-fixed-size';
        textarea.id = 'contextText' + index;
        textarea.textContent = context_text; // Initial content of the textarea
        textarea.name = context_id;
        // Create paragraph for file info
        const fileInfo = document.createElement('p');
        fileInfo.style.cssText = 'position: flex; margin-bottom: 0; margin-left: 3px; font-size: 0.75rem; margin-top: 0.3rem;';
        fileInfo.textContent = context_title 
    
        // Create the container for buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'buttons-container';
    
        // Create the 'Save context' button
        const saveButton = document.createElement('button');
        saveButton.type = 'submit';
        saveButton.className = 'btn btn-warning contextSubmit';
        saveButton.textContent = 'Update context';

        saveButton.id = context_id;
    
        // Create the trashcan button
        const trashcanButton = document.createElement('button');
        trashcanButton.type = 'submit';
        trashcanButton.className = 'trashcanButton btn btn-outline-danger';
        trashcanButton.textContent = 'Delete context';
        trashcanButton.name = context_id;
    
        // Append all elements to the buttons container
        buttonContainer.appendChild(saveButton);
        buttonContainer.appendChild(trashcanButton);
    
        // Append all elements to the main container
        contextsDiv.appendChild(textarea);
        contextsDiv.appendChild(fileInfo);
        contextsDiv.appendChild(buttonContainer);


        document.getElementById('contextText' + index).style.height = document.getElementById('contextText' + index).scrollHeight + "px";

    });

    const contextSubmitButtons = document.querySelectorAll('.contextSubmit');
    contextSubmitButtons.forEach(button => {
        button.addEventListener('click', updateContext);
    });

    const trashcantButtons = document.querySelectorAll('.trashcanButton');
    trashcantButtons.forEach(button => {
        button.addEventListener('click', trashcanClick);
    });

}
