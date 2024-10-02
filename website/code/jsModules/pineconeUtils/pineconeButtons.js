//Button handlers of all the pinecone related buttons that are on the answer info section

import { session } from '../sessionManager.js';
import { deletePineconeEmbedding, updatePineconeEmbedding, uploadPineconeEmbedding } from './pineconeFetches.js';
import { promptChange } from '../../script.js';

//Triggered by save to DB button - saves the original question and user edited answer as a pair to pineconeDB
export function saveToDB() {
    console.log("Saving to DB");

    if (confirm("Are you sure you want to save this q&a pair to the database? Check the sources and ensure your current answer is novel and generalized.")) {
        document.getElementById('loadingScreen').style.display = 'block'; // Show loading screen

        const selectedQA = session.qaList.find(item => item.id == session.highlightedQuestionId);

        const title = session.userName + "-" + session.projectTitle + "-" + getFormattedDate();
        const text = selectedQA.question + " - " + document.getElementById('alteredResponse').value;

        console.log(text);
        uploadPineconeEmbedding(title, text)
            .then(data => {
                alert("Q&a pair succesfully saved to DB");
                document.getElementById('loadingScreen').style.display = 'none'; 
            })
            .catch(error => {
                alert('Failed to upload to DB:', error);
                document.getElementById('loadingScreen').style.display = 'none'; 
            })
    }
}

//Updates the pineconeDB entry to reflect the chosen contexts textarea 
export async function updateContext(event) {
    if (confirm("Are you sure you want to update this context?")) {
        document.getElementById('loadingScreen').style.display = 'block'; 

        let buttonId = event.target.id;
        const title = "Edited:" + session.userName + "-" + getFormattedDate();
        let editedContext = document.getElementsByName(buttonId)[0].value;

        updatePineconeEmbedding(buttonId, editedContext, title)
            .then(async data => {
                if (confirm("Successfully updated this context. Would you like to regenerate your current answer with the updated context (your current answer will be reset)?")) {
                    await delay(250);
                    await promptChange()
                    .catch(err => {
                        throw new Error("Error during answer refresh: " + err.message);
                    });
                }
                return; 
            })
            .catch(error => {
                alert('Failed to upload to DB: ' + error.message);
                document.getElementById('loadingScreen').style.display = 'none';
            });
    }
}

//Deletes chosen context from pinecone db
export async function trashcanClick(event){
    if (confirm("Are you sure you want to delete this context?")) {
        document.getElementById('loadingScreen').style.display = 'block'; // Show loading screen

       let id = event.target.name;

        console.log("Deleting context with id: " + id);

        deletePineconeEmbedding(id)
        .then(async data => {
            if(confirm("Succesfully deleted this context. Would you like to regenerate your current answer with the deleted context (your current answer will be reset)?")){
                await delay(250);
                await promptChange()
                .catch(err => {
                    throw new Error("Error during answer refresh: " + err.message);
                });
            }
        })
        .catch(error => {
            alert('Failed to delete from DB:', error);
        })
    }
}

const delay = (delayInms) => {
    return new Promise(resolve => setTimeout(resolve, delayInms));
};

function getFormattedDate() {
    const date = new Date();
    let month = (date.getMonth() + 1).toString();
    let day = date.getDate().toString();
    const year = date.getFullYear();

    // Ensuring the month and day are two digits
    month = month.length < 2 ? '0' + month : month;
    day = day.length < 2 ? '0' + day : day;

    return `${month}/${day}/${year}`;
}