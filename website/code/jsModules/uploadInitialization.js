// Script that handles the submition of the uploade page and populates the DOM with all the questions and answers from the uploaded file.

import { session } from './sessionManager.js';
import { fillOutQuestionAnswers } from './retrieveLLMAnswer.js';
import { resetQAHeight } from '../script.js';

//Called when file uploaded - first parses questions out of excel sheet, then retrieves an llm answer for each question, then saves qa pairs to DOM
export function sendFile() {
    document.getElementById('uploadScreen').style.display = 'none';
    document.getElementById('loadingScreen').style.display = 'block';

    session.userName = document.getElementById('userName').value;
    session.projectTitle = document.getElementById('projectTitle').value;

    const fileInput = document.getElementById('excelFile');
    const file = fileInput.files[0];

    session.mainLLMInstructions = document.getElementById('llmInstructionTextArea').value;

    getQuestionsFromFile(file)
        .then(questions => fillOutQuestionAnswers(questions))
        .then(() => {
            // Do stuff with filled qaList
            addQAPairToDOM()
        })
        .catch(error => {
            console.log("ERRRORR:", error);
            alert("Failed to get LLM answers. Please retry file upload.")
        })
        .finally(() => {
            document.getElementById('loadingScreen').style.display = 'none'; 
            document.getElementById('exportButton').style.display = 'block';
        });
}

//Calls lambda function that takes in encoded excel spreadsheet and returns the first row as a list
async function getQuestionsFromFile(file){
    if (!file) {
        alert('Please select a file to upload.');
        return;
    }

    const reader = new FileReader();
        
    // Create a promise that resolves when the file is read
    const readPromise = new Promise((resolve, reject) => {
        reader.onload = () => {
            const base64Data = reader.result.split(',')[1]; 
            resolve(base64Data);
        };
        reader.onerror = () => reject('Failed to read the file.');
        reader.readAsDataURL(file);
    });

    const base64Data = await readPromise;

    for (let attempt = 1; attempt <= 3; attempt++) {
        try {
            const response = await fetch('https://xux7k8stx9.execute-api.us-east-2.amazonaws.com/sendFile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ body: base64Data })
            });

            const data = await response.json();
            console.log("Response was ok", data);
            return data;

        } catch (error) {
            console.error(`Attempt ${attempt} failed to get questionsFromAnswer:`, error);

            if(attempt == 3){
                throw error;
            }
        }
    }
}

//Takes in the session qaPair list and adds each qa pair to the DOM 
function addQAPairToDOM() {

    const scrollableLeft = document.querySelector('.QA');

    session.qaList.forEach((item, index) => {
        const qaPair = document.createElement('div');
        qaPair.classList.add('qa-pair');
        qaPair.id = index+1;

        const questionColumn = document.createElement('div');
        questionColumn.classList.add('half-column', 'question');
        const questionPara = document.createElement('p');
        questionPara.textContent = item.question;
        questionColumn.appendChild(questionPara);

        const answerColumn = document.createElement('div');
        answerColumn.classList.add('half-column', 'answer');
        const answerPara = document.createElement('p');
        answerPara.textContent = item.answer;
        answerColumn.appendChild(answerPara);

        qaPair.appendChild(questionColumn);
        qaPair.appendChild(answerColumn);

        scrollableLeft.appendChild(qaPair);
    });
    resetQAHeight();
}

document.getElementById('llmInstructionsPopupButton').addEventListener('click', function() {
    event.preventDefault();  // Prevent the default action
    document.getElementById('llmInstructionsPopup').style.display = 'block';
});

document.querySelector('.llmInstructionsPopup-close').addEventListener('click', function() {
    document.getElementById('llmInstructionsPopup').style.display = 'none';
});

window.onclick = function(event) {
    let modal = document.getElementById('llmInstructionsPopup');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}