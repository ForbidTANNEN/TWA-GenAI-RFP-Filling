import os
from dotenv import load_dotenv
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from vectorDB.scripts.utils.dataToDF import dataToDF
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()  # take environment variables from .env.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


#Tokenizer calculator function
def tiktoken_len(text):
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

def testChunker(filePath):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,  # Adjust based on the expected size of sections; this may need tuning
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""]  # Adjust this based on actual separators in your document
    )

    text = dataToDF(filePath).loc[0]["text"]
    split_text = text_splitter.split_text(text)
    for i, chunk in enumerate(split_text):
        if len(chunk) > 5:
            print(f"Chunk {i}:\n{chunk}\n")


def semanticTestChunker(filePath):
    text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="gradient", breakpoint_threshold_amount=70)

    text = dataToDF(filePath).loc[0]["text"]

    split_text = text_splitter.split_text(text)

    for i, chunk in enumerate(split_text):
        print(f"Chunk {i}:\n{chunk}\n")

testChunker("../cleanedUpData/TWA_Response_Peter_Lacke_digital_lab_Use_Cases.txt")








