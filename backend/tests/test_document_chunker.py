from backend.app.services.document_chunker import chunk_pages


def test_numbered_sections_remain_together():
    pages = [{
        "page_number": 1,
        "text": (
            "1. Policy Information\n"
            "Policy ID\nPOL-1001\n"
            "2. Covered Benefits\n"
            "Hospitalization\n"
            "Emergency treatment\n"
            "3. Exclusions\n"
            "Cosmetic procedures\n"
        ),
    }]

    chunks = chunk_pages(pages, source="policy.pdf")

    combined_text = "\n".join(chunk["text"] for chunk in chunks)

    assert "2. Covered Benefits" in combined_text
    assert "Hospitalization" in combined_text
    assert "3. Exclusions" in combined_text
    assert "Cosmetic procedures" in combined_text


def test_chunk_metadata_is_preserved():
    pages = [{
        "page_number": 2,
        "text": "1. Claim Assessment\nHuman review is required.",
    }]

    chunks = chunk_pages(pages, source="policy.pdf")

    assert chunks[0]["metadata"] == {
        "source": "policy.pdf",
        "page_number": 2,
        "chunk_number": 1,
    }


def test_invalid_chunk_size_is_rejected():
    try:
        chunk_pages([], source="policy.pdf", chunk_size=0)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_invalid_overlap_is_rejected():
    try:
        chunk_pages([], source="policy.pdf", chunk_size=100, overlap=100)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_oversized_section_uses_overlap_and_preserves_heading():
    pages = [{
        "page_number": 1,
        "text": "1. Covered Benefits\n" + " ".join(
            f"benefit{i}" for i in range(100)
        ),
    }]

    chunks = chunk_pages(
        pages,
        source="policy.pdf",
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all("1. Covered Benefits" in chunk["text"] for chunk in chunks)
    assert all(len(chunk["text"]) <= 100 for chunk in chunks)

    first_words = set(chunks[0]["text"].split())
    second_words = set(chunks[1]["text"].split())

    assert len(first_words & second_words) > 1
