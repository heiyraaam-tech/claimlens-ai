from fastapi import APIRouter, HTTPException

from backend.app.services.claim_loader import load_claims
from backend.app.services.policy_loader import load_policies
from backend.app.services.rules_engine.evaluator import evaluate_claim
from backend.app.schemas.rule_result import ClaimAssessment
from backend.app.schemas.ai_analysis import ClaimAIAnalysis

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])


@router.get("/")
def get_claims():
    return load_claims()


@router.post("/{claim_id}/assess", response_model=ClaimAssessment)
def assess_claim(claim_id: str):
    claims = load_claims()
    policies = load_policies()

    claim = next((c for c in claims if c.claim_id == claim_id), None)

    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")

    policy = next((p for p in policies if p.policy_id == claim.policy_id), None)

    if policy is None:
        raise HTTPException(status_code=404, detail="Associated policy not found")

    return evaluate_claim(claim, policy)


@router.post("/{claim_id}/analyze", response_model=ClaimAIAnalysis)
def analyze_claim_endpoint(claim_id: str):
    from backend.app.core.config import get_settings
    from backend.app.services.claim_ai_service import analyze_claim as run_ai_analysis

    settings = get_settings()

    if not settings.groq_api_key:
        raise HTTPException(
            status_code=503,
            detail="Groq API key is not configured.",
        )

    claims = load_claims()
    policies = load_policies()

    claim = next((c for c in claims if c.claim_id == claim_id), None)

    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")

    policy = next(
        (p for p in policies if p.policy_id == claim.policy_id),
        None,
    )

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Associated policy not found",
        )

    assessment = evaluate_claim(claim, policy)

    try:
        return run_ai_analysis(claim, policy, assessment)

    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
