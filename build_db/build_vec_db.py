"""
build_vec_db.py
"""
import os

import chromadb
from openai import AzureOpenAI
from langchain.document_loaders import PyPDFLoader

API_KEY = os.getenv("JODIE_API_KEY")
AZURE_ENDPOINT = os.getenv("JODIE_ENDPOINT")
API_VERSION = "2024-02-15-preview"
PDF_PATH = "/Users/dsaid/Desktop/wsg-proj/JoDIE/vectordb"

sync_client = AzureOpenAI(api_key=API_KEY,
                          azure_endpoint=AZURE_ENDPOINT,
                          api_version=API_VERSION)

# Function to get the embeddings
def get_embedding(text, engine="text-embedding-ada-002"):
   """
   Function to get the embeddings
   """
   embedding = sync_client.embeddings.create(input = text, model=engine).data[0].embedding
   return embedding

# Get the list of files in the directory
files = [f for f in os.listdir(PDF_PATH) if os.path.isfile(os.path.join(PDF_PATH, f))]
files.sort()

# Create a collection
chroma_client = chromadb.PersistentClient()
collection = chroma_client.create_collection(name="ICT_SS")

# Display the sorted files
for file in files:
    loader = PyPDFLoader(f"vectordb/{file}")
    pages = loader.load_and_split()
    num_pages = len(pages)
    for i in range(0, num_pages):
        print(i)
        content = pages[i].page_content
        doc_embedding = get_embedding(content)
        collection.add(
            documents=[content],
            embeddings=doc_embedding,
            metadatas=[{"source": f"{file}"}],
            ids=[f"{file}_pg{i}"])
