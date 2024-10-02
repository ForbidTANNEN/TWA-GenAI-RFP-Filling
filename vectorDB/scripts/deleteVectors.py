import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()  # take environment variables from .env.
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("twa-chatbot2")

# Function to delete vectors based on a metadata match
def delete_vectors_by_title(title):
    # Query vectors that have the specified title in their metadata
    for ids in index.list(prefix=title):
        print(ids)  # ['doc1#chunk1', 'doc1#chunk2', 'doc1#chunk3']
        index.delete(ids=ids)


# Call the function with the specific title
if __name__ == '__main__':
    delete_vectors_by_title("TWA Working Copy_UCDOPP5432.txt")