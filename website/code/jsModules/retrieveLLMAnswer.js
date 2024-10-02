// This file hosts the functions that are responsible for retrieving answers from the RAG LLM script deployed on AWS. 
// It send a list of queries and gets a list of answers in return.
//The apis go to the aws lambda script called twa-chatbot-LLMRetrieval which interacts with the RAG LLM model.

import { session } from './sessionManager.js';

const delay = (delayInms) => {
    return new Promise(resolve => setTimeout(resolve, delayInms));
};

export async function getAnswerFromQuestions(queries, maxRetries = 3) {
    const apiUrl = `https://xux7k8stx9.execute-api.us-east-2.amazonaws.com/query`;

    let failedAnswerCount = 0;
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ queries: queries, llmInstructions: session.mainLLMInstructions })
            });
        
            const data = await response.json();
            console.log(data);
            return data; 
        } catch (error) {
            console.error(`Attempt ${attempt} failed:`, error);
            failedAnswerCount++;
            if(failedAnswerCount == maxRetries){
                throw error;
            }
            else{
                await delay(250);
            }
        }
    }
}


export async function fillOutQuestionAnswers(questions) {

    let answers = await getAnswerFromQuestions(questions);

    
    const promises = answers.map((answer, index) => {

        let answerIsIDK = false;

        if (answer['answer'] == "I don't know.") {
            answerIsIDK = true;
        }

        return {
            id: index + 1,
            question: answer['query'],
            answer: answer['answer'],
            augmentedPrompt: answer['query'],
            context: answer['context'],
            answerIsIDK: answerIsIDK
        };

    });

    session.qaList = await Promise.all(promises); 
}