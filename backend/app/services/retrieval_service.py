from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore


class RetrievalService:
    def __init__(
        self,
        embedding_service=None,
        vector_store=None,
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        collection = self.vector_store.collection
        total_documents = collection.count()

        if total_documents == 0:
            return []

        query_embedding = self.embedding_service.generate_embeddings(
            [query.strip()]
        )[0]

        results = self.vector_store.search(
            query_embedding,
            top_k=min(top_k, total_documents),
        )

        retrieved = []

        for i, document in enumerate(results["documents"][0]):
            distance = results["distances"][0][i]

            retrieved.append({
                "chunk_id": results["ids"][0][i],
                "text": document,
                "metadata": results["metadatas"][0][i],
                "distance": distance,
                "similarity": max(0.0, min(1.0, 1.0 - distance)),
            })

        return retrieved


if __name__ == "__main__":
    from backend.app.services.pdf_extractor import extract_pdf_pages
    from backend.app.services.document_chunker import chunk_pages

    pdf_path = "data/documents/policies/policy_001.pdf"

    print("Extracting policy...")
    pages = extract_pdf_pages(pdf_path)

    print("Creating chunks...")
    chunks = chunk_pages(pages, source=pdf_path)

    print("Generating embeddings...")
    embedding_service = EmbeddingService()
    embeddings = embedding_service.generate_embeddings(
        [chunk["text"] for chunk in chunks]
    )

    print("Refreshing policy vectors...")
    vector_store = VectorStore()
    vector_store.add_documents(chunks, embeddings)

    print("Testing semantic retrieval...")
    retriever = RetrievalService(embedding_service, vector_store)

    queries = [
        "Are hospitalization expenses covered?",
        "Which medical procedures are excluded?",
        "What is the general waiting period?",
    ]

    for query in queries:
        print("\n" + "=" * 75)
        print("QUESTION:", query)

        results = retriever.retrieve(query, top_k=3)

        for result in results:
            print("\nChunk:", result["chunk_id"])
            print("Source:", result["metadata"]["source"])
            print("Page:", result["metadata"]["page_number"])
            print("Similarity:", round(result["similarity"], 4))
            print("Evidence:", result["text"][:500])

    print("\nRetrieval pipeline completed.")
