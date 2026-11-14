import pytest

from backend.app.services.claim_loader import load_claims
from backend.app.services.policy_loader import load_policies
from backend.app.services.rules_engine.evaluator import evaluate_claim


@pytest.fixture
def policy():
    return load_policies()[0]


@pytest.fixture
def claims():
    return load_claims()


def get_finding(assessment, rule_id):
    return next(
        finding
        for finding in assessment.findings
        if finding.rule_id == rule_id
    )


def test_hospitalization_matches_covered_benefit(policy, claims):
    claim = next(c for c in claims if c.claim_id == "CLM-5001")

    assessment = evaluate_claim(claim, policy)

    assert get_finding(assessment, "COVERAGE_CHECK").status == "pass"
    assert assessment.recommendation == "needs_human_review"


def test_cosmetic_procedure_triggers_exclusion(policy, claims):
    claim = next(c for c in claims if c.claim_id == "CLM-5002")

    assessment = evaluate_claim(claim, policy)

    assert get_finding(assessment, "EXCLUSION_CHECK").status == "fail"
    assert assessment.recommendation == "potentially_excluded"


def test_waiting_period_failure(policy, claims):
    claim = next(c for c in claims if c.claim_id == "CLM-5003")

    assessment = evaluate_claim(claim, policy)

    assert get_finding(assessment, "WAITING_PERIOD").status == "fail"
    assert assessment.recommendation == "potentially_excluded"


def test_wrong_policy_association_is_detected(policy, claims):
    claim = claims[0].model_copy(
        update={"policy_id": "POL-WRONG"}
    )

    assessment = evaluate_claim(claim, policy)

    assert get_finding(assessment, "POLICY_MATCH").status == "fail"
    assert assessment.recommendation == "needs_human_review"


def test_uncertain_exclusion_requires_human_review(policy, claims):
    claim = next(c for c in claims if c.claim_id == "CLM-5001")

    assessment = evaluate_claim(claim, policy)

    assert get_finding(assessment, "EXCLUSION_CHECK").status == "review"
    assert assessment.recommendation == "needs_human_review"


def test_exceeding_sum_insured_requires_human_review(policy, claims):
    claim = next(c for c in claims if c.claim_id == "CLM-5001")

    reduced_policy = policy.model_copy(
        update={"sum_insured": 1000}
    )

    assessment = evaluate_claim(claim, reduced_policy)

    assert get_finding(assessment, "SUM_INSURED_CHECK").status == "review"
    assert assessment.recommendation == "needs_human_review"
