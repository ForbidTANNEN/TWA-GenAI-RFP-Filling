import os
from uuid import uuid4
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from pinecone import Pinecone
from tqdm.auto import tqdm
from vectorDB.scripts.utils.dataToDF import dataToDF
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # take environment variables from .env.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

#-----CHUNK DATA Settings

tokenizer = tiktoken.get_encoding('cl100k_base')
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

#Break on backslash

def textSplitterType(typeOfSplitting: str):

    if(typeOfSplitting == "basic"):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=150,  # Adjust based on the expected size of sections; this may need tuning
            chunk_overlap=20,
            length_function=tiktoken_len,
            separators=["\n\n", "\n", " ", ""]  # Adjust this based on actual separators in your document
        )

    if(typeOfSplitting == "backslash"):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10,  # Adjust based on the expected size of sections; this may need tuning
            chunk_overlap=0,
            separators=["\\"]  # Adjust this based on actual separators in your document
        )

    if(typeOfSplitting == "semantic"):
        text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="gradient",
                                        breakpoint_threshold_amount=85)
    return text_splitter


text_splitter = textSplitterType(typeOfSplitting="backslash")

#-------EMBED DATA Settings


embed_model = "text-embedding-ada-002"

embed = OpenAIEmbeddings(
    model=embed_model,
    openai_api_key=OPENAI_API_KEY
)


##-------CREATE EMBEDDINGS

def createEmbeddings(df, index):
    batch_limit = 1
    texts = []
    metadatas = []

    for i, record in tqdm(df.iterrows(), total=df.shape[0]):
        # first get metadata fields for this record

        metadata = {
            'title': record['filename'].strip(".txt")
        }
        # now we create chunks from the record text
        record_texts = text_splitter.split_text(record['text'])

        for i, chunk in enumerate(record_texts):
            if len(chunk) <= 5:
                record_texts.pop(i)
        # create individual metadata dicts for each chunk
        record_metadatas = [{
            "chunk": j, "text": text.strip("\\"), **metadata
        } for j, text in enumerate(record_texts)]
        # append these to current batches
        texts.extend(record_texts)
        metadatas.extend(record_metadatas)
        # if we have reached the batch_limit we can add texts
        if len(texts) >= batch_limit:
            ids = [f"{record['filename']}_{datetime.now():%Y%m%d%H%M%S}_{uuid4().hex[:8]}" for _ in texts]
            embeds = embed.embed_documents(texts)  # Assuming embed is properly initialized
            index.upsert(vectors=list(zip(ids, embeds, metadatas)))  # Adjusting for Python 3
            texts = []
            metadatas = []

    # Handle any remaining texts
    if len(texts) > 0:
        ids = [str(uuid4()) for _ in range(len(texts))]
        embeds = embed.embed_documents(texts)
        index.upsert(vectors=list(zip(ids, embeds, metadatas)))

#PUT IN directory to upload whole directory or just a file
df = dataToDF("../cleanedUpData")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("twa-chatbot2")

print(df)
createEmbeddings(df, index)
