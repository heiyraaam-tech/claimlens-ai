from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()


if __name__ == "__main__":
    service = EmbeddingService()

    texts = [
        "Hospitalization expenses are covered under this policy.",
        "Cosmetic procedures are excluded from coverage.",
    ]

    vectors = service.generate_embeddings(texts)

    print("Embeddings generated:", len(vectors))
    print("Vector dimensions:", len(vectors[0]))
    print("First vector sample:", vectors[0][:5])
