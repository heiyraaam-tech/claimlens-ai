from backend.app.services.retrieval_evaluator import score_query


def test_relevant_result_at_rank_one():
    result = score_query(
        ["chunk_a"],
        [{"chunk_id": "chunk_a", "metadata": {"source": "policy.pdf", "page_number": 1}},
         {"chunk_id": "chunk_b", "metadata": {}}],
    )
    assert result["hit"] is True
    assert result["precision"] == 0.5
    assert result["recall"] == 1.0
    assert result["reciprocal_rank"] == 1.0
    assert result["attribution_accuracy"] == 1.0


def test_relevant_result_at_rank_three():
    result = score_query(
        ["chunk_c"],
        [{"chunk_id": "chunk_a", "metadata": {}},
         {"chunk_id": "chunk_b", "metadata": {}},
         {"chunk_id": "chunk_c", "metadata": {"source": "policy.pdf", "page_number": 1}}],
    )
    assert result["hit"] is True
    assert result["reciprocal_rank"] == 1 / 3


def test_no_relevant_result():
    result = score_query(
        ["chunk_expected"],
        [{"chunk_id": "chunk_other", "metadata": {}}],
    )
    assert result["hit"] is False
    assert result["recall"] == 0.0
    assert result["reciprocal_rank"] == 0.0
    assert result["attribution_accuracy"] is None


def test_multiple_expected_chunks():
    result = score_query(
        ["chunk_a", "chunk_b"],
        [{"chunk_id": "chunk_a", "metadata": {"source": "policy.pdf", "page_number": 1}}],
    )
    assert result["recall"] == 0.5
    assert result["precision"] == 1.0
