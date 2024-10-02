# Lambda script for twa-chatbot-uploadChunkToPinecone. This script is in charge of handling all pinecone index manipulations such as adding, editing, or deleting a specific vector

import json
import os
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from uuid import uuid4

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

embed_model = "text-embedding-ada-002"

embed = OpenAIEmbeddings(
    model=embed_model,
    openai_api_key=OPENAI_API_KEY
)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("twa-chatbot2")


def lambda_handler(event, context):
    body = json.loads(event['body'])
    print(body)

    if (body['change'] == 'add'):
        title = body['title']
        text = body['text']
        metadata = {
            'title': title,
            'chunk': 0,
            'text': text
        }

        id = f"{title}_{datetime.now():%Y%m%d%H%M%S}_{uuid4().hex[:8]}"
        embedding = embed.embed_documents([text])[0]
        index.upsert(vectors=[{
            "id": id,
            "values": embedding,
            "metadata": metadata,

        }])

        return {
            'statusCode': 200,
            'body': json.dumps("Succesfully saved with id: " + id)
        }

    if (body['change'] == 'update'):
        print("RANNNNN UPDATE")

        id = body['id']
        text = body['text']
        title = body['title']

        metadata = {
            'title': title,
            'chunk': 0,
            'text': text
        }
        embedding = embed.embed_documents([text])[0]
        print(embedding)

        index.upsert(vectors=[{
            "id": id,
            "values": embedding,
            "metadata": metadata,

        }])

        return {
            'statusCode': 200,
            'body': json.dumps("Succesfully updated id: " + id)
        }

    if (body['change'] == 'delete'):
        id = body["id"]
        index.delete(ids=[id])

        return {
            'statusCode': 200,
            'body': json.dumps("Succesfully deleted id: " + id)
        }

