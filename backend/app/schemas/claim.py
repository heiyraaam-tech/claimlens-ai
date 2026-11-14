from datetime import date
from pydantic import BaseModel, Field, model_validator


class Claim(BaseModel):
    claim_id: str
    policy_id: str
    claimant: str
    incident_date: date
    submission_date: date
    claim_type: str
    description: str
    hospital_name: str
    claimed_amount: float = Field(gt=0)
    currency: str = "INR"
    documents: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.submission_date < self.incident_date:
            raise ValueError(
                "Submission date cannot be before incident date"
            )
        return self
