import pytest

from backend.app.services.vector_store import VectorStore


class FakeCollection:
    def __init__(self, existing):
        self.existing = existing
        self.deleted = []
        self.upserted = None

    def get(self, where, include):
        source = where["source"]
        ids = [
            chunk_id
            for chunk_id, metadata in self.existing.items()
            if metadata["source"] == source
        ]
        return {"ids": ids}

    def delete(self, ids):
        self.deleted.extend(ids)
        for chunk_id in ids:
            self.existing.pop(chunk_id, None)

    def upsert(self, **kwargs):
        self.upserted = kwargs


def make_chunk(chunk_id, source):
    return {
        "chunk_id": chunk_id,
        "text": f"Content for {chunk_id}",
        "metadata": {
            "source": source,
            "page_number": 1,
            "chunk_number": 1,
        },
    }


def make_store(existing):
    store = VectorStore.__new__(VectorStore)
    store.collection = FakeCollection(existing)
    return store


def test_add_documents_removes_stale_chunks_for_same_source_only():
    existing = {
        "policy_old": {"source": "policy.pdf"},
        "policy_keep": {"source": "policy.pdf"},
        "other_policy": {"source": "other.pdf"},
    }
    store = make_store(existing)

    chunks = [make_chunk("policy_keep", "policy.pdf")]
    store.add_documents(chunks, [[0.1, 0.2]])

    assert store.collection.deleted == ["policy_old"]
    assert "other_policy" in store.collection.existing
    assert store.collection.upserted["ids"] == ["policy_keep"]


def test_add_documents_handles_multiple_sources_independently():
    existing = {
        "old_a": {"source": "a.pdf"},
        "old_b": {"source": "b.pdf"},
    }
    store = make_store(existing)

    chunks = [
        make_chunk("new_a", "a.pdf"),
        make_chunk("new_b", "b.pdf"),
    ]
    store.add_documents(chunks, [[0.1], [0.2]])

    assert set(store.collection.deleted) == {"old_a", "old_b"}
    assert store.collection.upserted["ids"] == ["new_a", "new_b"]


def test_add_documents_rejects_mismatched_embeddings():
    store = make_store({})

    with pytest.raises(ValueError, match="one embedding"):
        store.add_documents(
            [make_chunk("chunk_1", "policy.pdf")],
            [],
        )


def test_add_documents_does_not_delete_when_input_is_empty():
    store = make_store({"existing": {"source": "policy.pdf"}})

    store.add_documents([], [])

    assert store.collection.deleted == []
    assert store.collection.upserted is None
