from datetime import date

from pydantic import BaseModel, Field, model_validator


class Policy(BaseModel):
    policy_id: str
    policyholder: str
    policy_type: str
    provider: str

    effective_date: date
    expiry_date: date

    sum_insured: float = Field(gt=0)
    deductible: float = Field(ge=0)
    waiting_period_days: int = Field(ge=0)

    covered_benefits: list[str]
    exclusions: list[str]

    currency: str = "INR"

    @model_validator(mode="after")
    def validate_policy(self):
        if self.expiry_date < self.effective_date:
            raise ValueError("Policy expiry date cannot be before effective date")

        if self.deductible > self.sum_insured:
            raise ValueError("Deductible cannot exceed sum insured")

        return self
