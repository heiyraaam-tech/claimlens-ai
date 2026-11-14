from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.ai_analysis import ClaimAIAnalysis, EvidenceSource
from backend.app.schemas.rule_result import ClaimAssessment, RuleFinding

client = TestClient(app)


def mock_settings(api_key="test-groq-key"):
    return SimpleNamespace(groq_api_key=api_key)


def mock_analysis(*args):
    return ClaimAIAnalysis(
        claim_id="CLM-5001",
        policy_id="POL-1001",
        rule_assessment=ClaimAssessment(
            claim_id="CLM-5001",
            policy_id="POL-1001",
            findings=[
                RuleFinding(
                    rule_id="POLICY_MATCH",
                    status="pass",
                    message="Policy association verified.",
                )
            ],
            recommendation="needs_human_review",
        ),
        analysis="Synthetic test analysis. Human review is required.",
        sources=[
            EvidenceSource(
                chunk_id="policy_001_p1_c2",
                source="policy_001.pdf",
                page_number=1,
                similarity=0.85,
                text="Hospitalization is listed as a covered benefit.",
            )
        ],
        human_review_required=True,
    )


def test_analyze_claim_returns_valid_response(monkeypatch):
    monkeypatch.setattr(
        "backend.app.core.config.get_settings",
        lambda: mock_settings(),
    )
    monkeypatch.setattr(
        "backend.app.services.claim_ai_service.analyze_claim",
        mock_analysis,
    )

    response = client.post("/api/v1/claims/CLM-5001/analyze")

    assert response.status_code == 200
    data = response.json()
    assert data["claim_id"] == "CLM-5001"
    assert data["policy_id"] == "POL-1001"
    assert data["human_review_required"] is True
    assert data["sources"][0]["chunk_id"] == "policy_001_p1_c2"
    assert data["disclaimer"]


def test_analyze_unknown_claim_returns_404(monkeypatch):
    monkeypatch.setattr(
        "backend.app.core.config.get_settings",
        lambda: mock_settings(),
    )

    response = client.post("/api/v1/claims/UNKNOWN/analyze")

    assert response.status_code == 404
    assert response.json()["detail"] == "Claim not found"


def test_analyze_without_groq_key_returns_503(monkeypatch):
    monkeypatch.setattr(
        "backend.app.core.config.get_settings",
        lambda: mock_settings(api_key=None),
    )

    response = client.post("/api/v1/claims/CLM-5001/analyze")

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_analyze_groq_value_error_returns_503(monkeypatch):
    monkeypatch.setattr(
        "backend.app.core.config.get_settings",
        lambda: mock_settings(),
    )

    def fail_analysis(*args):
        raise ValueError("AI configuration problem")

    monkeypatch.setattr(
        "backend.app.services.claim_ai_service.analyze_claim",
        fail_analysis,
    )

    response = client.post("/api/v1/claims/CLM-5001/analyze")

    assert response.status_code == 503
    assert response.json()["detail"] == "AI configuration problem"


def test_analyze_groq_runtime_error_returns_502(monkeypatch):
    monkeypatch.setattr(
        "backend.app.core.config.get_settings",
        lambda: mock_settings(),
    )

    def fail_analysis(*args):
        raise RuntimeError("Groq service unavailable")

    monkeypatch.setattr(
        "backend.app.services.claim_ai_service.analyze_claim",
        fail_analysis,
    )

    response = client.post("/api/v1/claims/CLM-5001/analyze")

    assert response.status_code == 502
    assert response.json()["detail"] == "Groq service unavailable"
