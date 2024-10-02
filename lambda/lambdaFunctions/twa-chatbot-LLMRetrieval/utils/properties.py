import os
from dotenv import load_dotenv


class Properties:
    def __init__(self):
        self.load_keys()

    def is_aws_environment(self):
        # Checks if running in an AWS Lambda environment
        return (os.getenv("AWS") == "True")

    def load_keys(self):
        if self.is_aws_environment():
            self.PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "default_pinecone_key")
            self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "default_openai_key")
            self.COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "default_cohere_key")
        else:
            load_dotenv()
            self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "default_pinecone_key")
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default_openai_key")
            self.COHERE_API_KEY = os.getenv("COHERE_API_KEY", "default_cohere_key")


