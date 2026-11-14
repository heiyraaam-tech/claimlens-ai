import json
from pathlib import Path
from statistics import mean


def score_query(expected_chunk_ids: list[str], retrieved: list[dict]) -> dict:
    expected = set(expected_chunk_ids)
    retrieved_ids = [item["chunk_id"] for item in retrieved]
    relevant_ranks = [
        rank
        for rank, chunk_id in enumerate(retrieved_ids, start=1)
        if chunk_id in expected
    ]

    relevant_found = len(set(retrieved_ids) & expected)
    precision = relevant_found / len(retrieved_ids) if retrieved_ids else 0.0
    recall = relevant_found / len(expected) if expected else 0.0
    reciprocal_rank = 1 / relevant_ranks[0] if relevant_ranks else 0.0

    matched_results = [
        item for item in retrieved if item["chunk_id"] in expected
    ]
    correctly_attributed = sum(
        bool(item.get("metadata", {}).get("source"))
        and item.get("metadata", {}).get("page_number") is not None
        for item in matched_results
    )
    attribution_accuracy = (
        correctly_attributed / len(matched_results)
        if matched_results else None
    )

    return {
        "hit": bool(relevant_ranks),
        "precision": precision,
        "recall": recall,
        "reciprocal_rank": reciprocal_rank,
        "relevant_found": relevant_found,
        "expected_count": len(expected),
        "retrieved_chunk_ids": retrieved_ids,
        "relevant_ranks": relevant_ranks,
        "attribution_accuracy": attribution_accuracy,
    }


def evaluate_dataset(dataset_path: Path, k: int = 3) -> dict:
    from backend.app.services.retrieval_service import RetrievalService

    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    retriever = RetrievalService()

    results = []
    for item in dataset:
        retrieved = retriever.retrieve(item["question"], top_k=k)
        score = score_query(item["expected_chunk_ids"], retrieved)
        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected_chunk_ids": item["expected_chunk_ids"],
            **score,
        })

    attribution_scores = [
        item["attribution_accuracy"]
        for item in results
        if item["attribution_accuracy"] is not None
    ]

    summary = {
        "questions_evaluated": len(results),
        "k": k,
        "hit_rate_at_k": mean(item["hit"] for item in results),
        "precision_at_k": mean(item["precision"] for item in results),
        "recall_at_k": mean(item["recall"] for item in results),
        "mrr_at_k": mean(item["reciprocal_rank"] for item in results),
        "evidence_attribution_accuracy": (
            mean(attribution_scores) if attribution_scores else None
        ),
    }

    return {"summary": summary, "results": results}
