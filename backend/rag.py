from fastapi import APIRouter, File, UploadFile, HTTPException
import faiss
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import docx
import numpy as np
from typing import List
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()
router = APIRouter()

# Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY_RAG"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_RAG")
)

AZURE_EMBEDDING_MODEL = "text-embedding-ada-002"

# FAISS setup
embedding_dim = 1536  # ADA-002
index = faiss.IndexFlatL2(embedding_dim)

# Metadata
documents: List[str] = []
MAX_DOCS = 2000       # Cap on total chunks
MAX_PDF_SIZE_MB = 10  # PDF file size limit

def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[-1].lower()
    text = ""
    if ext == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif ext == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file type")
    return text

def get_azure_embeddings(texts: List[str]) -> np.ndarray:
    response = client.embeddings.create(
        model=AZURE_EMBEDDING_MODEL,
        input=texts
    )
    embeddings = [item.embedding for item in response.data]
    return np.array(embeddings, dtype=np.float32)

@router.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...)):
    # Validate PDF size before saving
    if file.filename.lower().endswith(".pdf"):
        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_PDF_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"PDF exceeds size limit of {MAX_PDF_SIZE_MB} MB"
            )
        # Rewind file pointer for saving
        file.file.seek(0)

    # Save uploaded file
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text
    text = extract_text_from_file(file_path)

    # Chunk text
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = splitter.split_text(text)

    # Get embeddings from Azure
    embeddings = get_azure_embeddings(chunks)

    # Cap FAISS index size
    global documents, index
    excess = (len(documents) + len(chunks)) - MAX_DOCS
    if excess > 0:
        keep_idx = list(range(excess, len(documents)))
        vectors = np.array([index.reconstruct(i) for i in keep_idx], dtype=np.float32)
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(vectors)
        documents = documents[excess:]

    # Add new data
    index.add(embeddings)
    documents.extend(chunks)

    # Cleanup
    os.remove(file_path)

    return {
        "status": "success",
        "chunks_added": len(chunks),
        "total_chunks": len(documents)
    }


def build_sora_prompt(query: str, top_k: int = 1) -> str:
    if index.ntotal == 0:
        return query  # Just return the raw query

    query_emb = get_azure_embeddings([query])
    distances, indices = index.search(query_emb, top_k)
    valid_idxs = [i for i in indices[0] if 0 <= i < len(documents)]
    if not valid_idxs:
        return query

    # Merge and clean retrieved context
    context_text = " ".join(clean_context(documents[i]) for i in valid_idxs)
    
    # Combine naturally
    return f"{query} {context_text}"


import re

def clean_context(text: str) -> str:
    # Remove emails, phone numbers, and URLs
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'\+?\d[\d\s-]{7,}', '', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\s+', ' ', text)  # collapse whitespace
    return text.strip()

@router.post("/test-prompt")
def test_prompt(data: str):
    final_prompt = build_sora_prompt(data)
    return {"prompt": final_prompt}
