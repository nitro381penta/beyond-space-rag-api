import os
import uuid
import chromadb

from app.config import (
    CHROMA_PATH,
    CHROMA_COLLECTION_NAME,
    DOCS_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from app.embeddings import embed_texts

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

def list_markdown_files(root_dir: str) -> list[str]:
    paths = []
    for base, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".md"):
                paths.append(os.path.join(base, f))
    return sorted(paths)

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks

def build_metadata(file_path: str, chunk_index: int) -> dict:
    rel_path = os.path.relpath(file_path, DOCS_PATH).replace("\\", "/")
    parts = rel_path.split("/")
    category = parts[0] if len(parts) > 1 else "unknown"
    filename = os.path.splitext(parts[-1])[0]

    return {
        "source": rel_path,
        "category": category,
        "filename": filename,
        "chunk_index": chunk_index,
    }

def rebuild_index() -> dict:
    collection = get_collection()

    existing = collection.get()
    existing_ids = existing.get("ids", [])
    if existing_ids:
        collection.delete(ids=existing_ids)

    file_paths = list_markdown_files(DOCS_PATH)

    all_ids = []
    all_docs = []
    all_meta = []

    for file_path in file_paths:
        text = read_text(file_path)
        chunks = split_into_chunks(text)

        for idx, chunk in enumerate(chunks):
            all_ids.append(str(uuid.uuid4()))
            all_docs.append(chunk)
            all_meta.append(build_metadata(file_path, idx))

    if not all_docs:
        return {"documents_indexed": 0, "chunks_indexed": 0}

    embeddings = embed_texts(all_docs)

    collection.add(
        ids=all_ids,
        documents=all_docs,
        metadatas=all_meta,
        embeddings=embeddings,
    )

    return {
        "documents_indexed": len(file_paths),
        "chunks_indexed": len(all_docs),
    }