from pathlib import Path
import os

import fitz
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from research_assistant.config import base_paper_path, chroma_path


COLLECTION_NAME = "base_paper"


def retrieve_base_context(query: str, limit: int = 4) -> list[str]:
    paper_path = base_paper_path()
    if not paper_path:
        return []
    if not paper_path.exists():
        return [f"Base paper PDF not found at {paper_path}."]
    if not os.getenv("OPENAI_API_KEY"):
        return ["Base paper retrieval needs OPENAI_API_KEY for text-embedding-3-small."]

    vector_store = _load_or_build_vector_store(paper_path)
    results = vector_store.similarity_search(query, k=limit)
    return [result.page_content for result in results]


def _load_or_build_vector_store(paper_path: Path):
    from langchain_chroma import Chroma

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    persist_dir = chroma_path()
    collection_metadata = {"paper_path": str(paper_path.resolve())}
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
        collection_metadata=collection_metadata,
    )

    if vector_store._collection.count() == 0:
        chunks = _chunk_pdf(paper_path)
        if chunks:
            vector_store.add_texts(
                chunks,
                metadatas=[{"source": str(paper_path), "chunk": index} for index, _ in enumerate(chunks)],
            )

    return vector_store


def _chunk_pdf(paper_path: Path) -> list[str]:
    text = _extract_pdf_text(paper_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    return splitter.split_text(text)


def _extract_pdf_text(paper_path: Path) -> str:
    with fitz.open(paper_path) as document:
        pages = [page.get_text("text") for page in document]
    return "\n".join(pages).strip()
