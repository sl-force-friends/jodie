import os
import chromadb
from openai import AzureOpenAI
from langchain.document_loaders import PyPDFLoader
API_KEY = os.getenv("JODIE_API_KEY")
AZURE_ENDPOINT = os.getenv("JODIE_ENDPOINT")
API_VERSION = "2024-02-15-preview"
sync_client = AzureOpenAI(api_key=API_KEY,
                          azure_endpoint=AZURE_ENDPOINT,
                          api_version=API_VERSION)
def get_embedding(text, engine="text-embedding-ada-002"):
   embeddings = sync_client.embeddings.create(input = text, model=engine).data[0].embedding
   return embeddings
directory_path = "/Users/dsaid/Desktop/wsg-proj/JoDIE/vectordb"
files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
files.sort()
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
        embeddings = get_embedding(content)
        collection.add(
            documents=[content],
            embeddings=embeddings,
            metadatas=[{"source": f"{file}"}],
            ids=[f"{file}_pg{i}"])