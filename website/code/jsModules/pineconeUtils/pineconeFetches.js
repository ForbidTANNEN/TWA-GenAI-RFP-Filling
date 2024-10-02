//Functions that manipulate the pinecone database instance. 
// All api calls go to the aws script called twa-chatbot-uploadChunkToPinecone which directly interact with the pinecone database.

export async function deletePineconeEmbedding(id){
    const response = await fetch('https://xux7k8stx9.execute-api.us-east-2.amazonaws.com/uploadPineconeEmbedding', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ change: 'delete', id: id })
    });

    const data = await response.json(); 
    console.log(data);
    return data; 
}

export async function updatePineconeEmbedding(id, text, title){
    const response = await fetch('https://xux7k8stx9.execute-api.us-east-2.amazonaws.com/uploadPineconeEmbedding', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ change: 'update', id: id, text: text, title: title })
    });

    const data = await response.json(); 
    console.log(data);
    console.log("Updated context with id: " + id);
    return data; 
}

export async function uploadPineconeEmbedding(title, text){
    const response = await fetch('https://xux7k8stx9.execute-api.us-east-2.amazonaws.com/uploadPineconeEmbedding', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ change: 'add', title: title, text: text })
    });

    const data = await response.json(); 
    console.log(data);
    return data; 
}