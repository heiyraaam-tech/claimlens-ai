import chromadb
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "vector_db"


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(DB_PATH))
        self.collection = self.client.get_or_create_collection(
            name="policy_documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, chunks, embeddings):
        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise ValueError("Each document chunk must have one embedding.")

        chunks_by_source = defaultdict(list)

        for chunk in chunks:
            source = chunk["metadata"].get("source")
            if not source:
                raise ValueError("Every chunk must include a source in its metadata.")
            chunks_by_source[source].append(chunk)

        # Reconcile each source independently to preserve other documents.
        for source, source_chunks in chunks_by_source.items():
            fresh_ids = {chunk["chunk_id"] for chunk in source_chunks}

            existing = self.collection.get(
                where={"source": source},
                include=["metadatas"],
            )

            stale_ids = [
                chunk_id
                for chunk_id in existing["ids"]
                if chunk_id not in fresh_ids
            ]

            if stale_ids:
                self.collection.delete(ids=stale_ids)

        self.collection.upsert(
            ids=[chunk["chunk_id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks],
        )

    def search(self, query_embedding, top_k=3):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
