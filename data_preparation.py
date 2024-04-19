import os
from dotenv import load_dotenv
import pymongo
import pandas as pd
from mistralai.client import MistralClient
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Now you can safely use os.environ to access your variables
api_key = os.environ.get("MISTRAL_API_KEY")
mongo_uri = os.environ.get("MONGO_URI")

def connect_mongodb():
    client = pymongo.MongoClient(mongo_uri)
    db = client["vector-database"]
    collection = db["vector-collection"]
    return collection

def get_embedding(text, client):
    text = text.replace("\n", " ")
    embeddings_batch_response = client.embeddings(
        model="mistral-embed",
        input=text,
    )
    return embeddings_batch_response.data[0].embedding

def data_prep(file_path):
    # Set up Mistral client
    client = MistralClient(api_key=api_key)

    # Process the uploaded file
    loader = PyPDFLoader(file_path)  # Pass the file path directly
    pages = loader.load_and_split()  # Load and split the PDF into pages

    # Split data
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""],
        length_function=len,
    )
    docs = text_splitter.split_documents(pages)

    # Calculate embeddings and store into MongoDB
    text_chunks = [text.page_content for text in docs]
    df = pd.DataFrame({'text_chunks': text_chunks})
    df['embedding'] = df.text_chunks.apply(lambda x: get_embedding(x, client))

    collection = connect_mongodb()
    df_dict = df.to_dict(orient='records')
    collection.insert_many(df_dict)

    return "PDF processed and data stored in MongoDB."

# Assuming the PDF file path is provided via command line
if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'sample.pdf'
    print(data_prep(file_path))
