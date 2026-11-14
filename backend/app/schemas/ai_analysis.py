from typing import Literal
from pydantic import BaseModel

from backend.app.schemas.rule_result import ClaimAssessment


class EvidenceSource(BaseModel):
    chunk_id: str
    source: str
    page_number: int
    similarity: float
    text: str


class ClaimAIAnalysis(BaseModel):
    claim_id: str
    policy_id: str
    rule_assessment: ClaimAssessment
    analysis: str
    sources: list[EvidenceSource]
    human_review_required: bool = True
    disclaimer: str = (
        "AI-generated analysis is advisory only. "
        "Final claim decisions require authorized human review."
    )
