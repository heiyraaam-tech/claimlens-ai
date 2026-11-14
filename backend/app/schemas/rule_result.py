from typing import Literal

from pydantic import BaseModel


class RuleFinding(BaseModel):
    rule_id: str
    status: Literal["pass", "fail", "review"]
    message: str


class ClaimAssessment(BaseModel):
    claim_id: str
    policy_id: str
    findings: list[RuleFinding]

    recommendation: Literal[
        "potentially_covered",
        "potentially_excluded",
        "needs_human_review",
    ]
