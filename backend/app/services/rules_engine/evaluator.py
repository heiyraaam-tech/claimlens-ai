from backend.app.schemas.claim import Claim
from backend.app.schemas.policy import Policy
from backend.app.schemas.rule_result import ClaimAssessment, RuleFinding


def normalize_term(value: str) -> str:
    words = value.strip().casefold().split()
    normalized = []

    for word in words:
        if word.endswith("ies") and len(word) > 3:
            word = word[:-3] + "y"
        elif word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]

        normalized.append(word)

    return " ".join(normalized)


def evaluate_claim(claim: Claim, policy: Policy) -> ClaimAssessment:
    findings = []

    policy_match = claim.policy_id == policy.policy_id
    findings.append(RuleFinding(
        rule_id="POLICY_MATCH",
        status="pass" if policy_match else "fail",
        message="Policy association verified." if policy_match
        else "Claim policy ID does not match."
    ))

    policy_active = policy.effective_date <= claim.incident_date <= policy.expiry_date
    findings.append(RuleFinding(
        rule_id="POLICY_PERIOD",
        status="pass" if policy_active else "fail",
        message="Policy active on incident date." if policy_active
        else "Incident occurred outside policy period."
    ))

    days_elapsed = (claim.incident_date - policy.effective_date).days
    waiting_met = days_elapsed >= policy.waiting_period_days
    findings.append(RuleFinding(
        rule_id="WAITING_PERIOD",
        status="pass" if waiting_met else "fail",
        message=f"{days_elapsed} days elapsed; required {policy.waiting_period_days} days."
    ))

    claim_type = normalize_term(claim.claim_type)

    excluded = any(
        normalize_term(item) == claim_type
        for item in policy.exclusions
    )

    findings.append(RuleFinding(
        rule_id="EXCLUSION_CHECK",
        status="fail" if excluded else "review",
        message="Claim matches an explicit exclusion."
        if excluded else "No normalized exclusion match; further interpretation required."
    ))

    covered = any(
        normalize_term(item) == claim_type
        for item in policy.covered_benefits
    )

    findings.append(RuleFinding(
        rule_id="COVERAGE_CHECK",
        status="pass" if covered else "review",
        message="Claim matches a listed benefit."
        if covered else "No normalized covered-benefit match found."
    ))

    currency_match = claim.currency.strip().upper() == policy.currency.strip().upper()
    findings.append(RuleFinding(
        rule_id="CURRENCY_CHECK",
        status="pass" if currency_match else "fail",
        message="Currencies match." if currency_match
        else "Claim and policy currencies differ."
    ))

    amount_within_limit = claim.claimed_amount <= policy.sum_insured
    findings.append(RuleFinding(
        rule_id="SUM_INSURED_CHECK",
        status="pass" if amount_within_limit else "review",
        message="Claim is within sum insured."
        if amount_within_limit else "Claim exceeds sum insured; financial review required."
    ))

    if not policy_match or not policy_active or not currency_match:
        recommendation = "needs_human_review"
    elif excluded or not waiting_met:
        recommendation = "potentially_excluded"
    elif (
        any(finding.status == "review" for finding in findings)
        or any(finding.status == "fail" for finding in findings)
    ):
        recommendation = "needs_human_review"
    else:
        recommendation = "potentially_covered"

    return ClaimAssessment(
        claim_id=claim.claim_id,
        policy_id=claim.policy_id,
        findings=findings,
        recommendation=recommendation,
    )
