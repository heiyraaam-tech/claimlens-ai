from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.pdf_extractor import extract_pdf_pages
from backend.app.services.document_chunker import chunk_pages
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore

def main():
    pdf = ROOT / "data/documents/policies/policy_001.pdf"
    pages = extract_pdf_pages(pdf)
    chunks = chunk_pages(
        pages,
        source="data/documents/policies/policy_001.pdf",
    )

    if not chunks:
        raise RuntimeError("No policy chunks created.")

    print("Pages:", len(pages))
    print("Chunks:", len(chunks))
    print("Generating embeddings...")

    embedding_service = EmbeddingService()
    embeddings = embedding_service.generate_embeddings(
        [chunk["text"] for chunk in chunks]
    )

    store = VectorStore()
    store.add_documents(chunks, embeddings)

    print("INGESTION COMPLETE")
    print("Indexed chunks:", store.collection.count())

if __name__ == "__main__":
    main()
