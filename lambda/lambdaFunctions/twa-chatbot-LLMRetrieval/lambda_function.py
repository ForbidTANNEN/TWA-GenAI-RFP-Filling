# Lambda script for twa-chatbot-LLMRetrieval. The main RAG llm script that utilizes pineconedb and openAI to get contextually accurate LLM answers.

from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from openai import OpenAI
from utils.properties import Properties
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

config = Properties()
OPENAI_API_KEY = config.OPENAI_API_KEY
PINECONE_API_KEY = config.PINECONE_API_KEY

openAIClient = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index("twa-chatbot2")

embed_model = "text-embedding-ada-002"

embed = OpenAIEmbeddings(
    model=embed_model,
    openai_api_key=OPENAI_API_KEY
)

#Given a primer and query returns llm answer
def getLLMResponse(primer, query):
    res = openAIClient.chat.completions.create(model="gpt-4o",
        messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": query}
                ])
    return res.choices[0].message.content

#Given a generic query, creates a hyde query and generates and returns llms response
def hydeQuery(query):
    hyde_primer = (
        "You are an advanced AI that writes a short hypothetical answer to a prompt. Write it what you think thirdwaves analytics, a LIMS company, would write in response to a vendor questionaire.\n")
    hyde_augemented_question = "-----\nQuestion: " + query + "\nAnswer:"

    hyde_answer = query + " - " + getLLMResponse(hyde_primer, hyde_augemented_question)
    return hyde_answer

#Given a query and context, builds LLM prompt and returns its answer
def LLMResponseFromContext(query, context_res, llmInstructions):
    contexts = [item['metadata']['text'] for item in context_res]

    augmented_query = "---\n".join(
        contexts) + "\n-----\n" + "Vendor Question: " + query + "\nYour answer (use only facts from the context above to answer and follow the guidelines):"

    primer = f"""
     As an advanced AI, your role is to assist ThirdWave Analytics by providing formal responses to inquiries from prospective vendors. Follow these guidelines:
    {llmInstructions}
    Previous vendor questionaire answers: 
    """

    llmAnswer = getLLMResponse(primer, augmented_query)
    return llmAnswer

# Given a dictionary of context, removes any duplicated entries
def unduplicateContext(context_res):
    idList = []
    finalList = []

    for context in context_res:
        context_id = context["id"]
        if(context_id not in idList):
            idList.append(context_id)
            finalList.append(context)
    return finalList

#Given a query and a set of instructions on how to answer - returns a dictionary consisting of the query, a contextually accurate answer, and the context utilized.
def queryRetrieval(query, llmInstructions):

    # Hyde pinecone embedding results
    hyde_xq = embed.embed_query(hydeQuery(query))
    hyde_context_res = index.query(vector=hyde_xq, top_k=3, include_metadata=True)

    # Basic query pinecone results
    xq = embed.embed_query(query)
    real_context_res = index.query(vector=xq, top_k=5, include_metadata=True)

    #Combining hyde query and reg query into one object
    context_res = real_context_res['matches'] + hyde_context_res['matches']
    context_res = unduplicateContext(context_res)

    #Get llm answer based on context
    llmAnswer = LLMResponseFromContext(query, context_res, llmInstructions)

    #Simplify context to only needed info
    simplified_context = [{
        'text': item['metadata']['text'],
        'title': item['metadata']['title'],
        'score': item['score'],
        'id': item['id']
    } for item in context_res]

    return {"query": query, "answer": llmAnswer, "context": simplified_context}


# - AWS handler
def lambda_handler(event, context):
    body = json.loads(event['body'])
    queries = body['queries']

    llmInstructions = body['llmInstructions']

    qaPairs = []

    # Create a ThreadPoolExecutor to manage a pool of threads
    num_threads = min(len(queries), 10)
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit tasks to the executor
        futures = {executor.submit(queryRetrieval, query, llmInstructions): query for query in queries}

        for future in as_completed(futures):
            queryAnswer = future.result()
            qaPairs.append(queryAnswer)

    return {
        "statusCode": 200,
        "body": json.dumps(qaPairs, indent=4)
    }


#- If local
if __name__ == '__main__':
    llmInstructions = f"""
        -If the context provided is insufficient for a detailed response, simply state "I don't know."
        -Be aware that the supplied context might be outdated or irrelevant, ignore dates.
        -Answer directly and solely in relation to the question posed, avoiding unnecessary information.
        -Do not include any references to other "previously answered questions, or "attached documents".
        -Ensure smooth flow and connectivity between sentences, favoring longer, well-constructed sentences over shorter, disjointed ones.
        -Focus soley on the question and answering. Just take small parts of the context as needed.
        -Only include information relevant to the given question.
        -Aim to present your answers in a human-like manner, very easy to read.
        -Answer very short and concise. No need to explain abreviations - be to the point and only answer the question. A couple sentences max.
        -Ensure to break the question down and answer in multiple steps. Answer in the same fashion as the question. Ensure every subquestion asked in the question is answered or says I dont know.
    """
    print(queryRetrieval("Does lockbox LIMS allow different user permissions?", llmInstructions));