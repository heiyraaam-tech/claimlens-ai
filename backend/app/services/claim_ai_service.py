import json
import urllib.error
import urllib.request

from backend.app.core.config import get_settings
from backend.app.schemas.ai_analysis import (
    ClaimAIAnalysis,
    EvidenceSource,
)
from backend.app.schemas.claim import Claim
from backend.app.schemas.policy import Policy
from backend.app.schemas.rule_result import ClaimAssessment
from backend.app.services.retrieval_service import RetrievalService


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def analyze_claim(
    claim: Claim,
    policy: Policy,
    assessment: ClaimAssessment,
) -> ClaimAIAnalysis:

    settings = get_settings()

    if not settings.groq_api_key:
        raise ValueError(
            "Groq API key missing. Configure CLAIMLENS_GROQ_API_KEY in .env."
        )

    retriever = RetrievalService()

    query = (
        f"Insurance policy evidence for claim type: {claim.claim_type}. "
        f"Claim description: {claim.description}. "
        "Find relevant coverage, exclusions, waiting periods and limits."
    )

    retrieved = retriever.retrieve(query, top_k=4)

    sources = [
        EvidenceSource(
            chunk_id=item["chunk_id"],
            source=item["metadata"]["source"],
            page_number=item["metadata"]["page_number"],
            similarity=item["similarity"],
            text=item["text"],
        )
        for item in retrieved
    ]

    evidence = [
        {
            "chunk_id": item.chunk_id,
            "page": item.page_number,
            "text": item.text,
        }
        for item in sources
    ]

    prompt = f"""
You are ClaimLens AI, an insurance policy evidence analyst.

Analyze the supplied insurance claim using ONLY the supplied policy
evidence and deterministic rule assessment.

IMPORTANT SAFEGUARDS:
- Never invent policy clauses or coverage conditions.
- Never assume missing information.
- Distinguish explicit policy evidence from uncertainty.
- Do not independently approve or reject a claim.
- Explain relevant coverage, exclusions, waiting periods and limits.
- Identify contradictions or missing evidence.
- If evidence is insufficient, explicitly say so.
- Treat the rules assessment as a separate deterministic input.
- Recommend human review for ambiguous or incomplete information.
- Do not treat similarity scores as probabilities.

CLAIM:
{json.dumps(claim.model_dump(mode="json"), indent=2)}

POLICY:
{json.dumps(policy.model_dump(mode="json"), indent=2)}

DETERMINISTIC RULE ASSESSMENT:
{json.dumps(assessment.model_dump(mode="json"), indent=2)}

RETRIEVED POLICY EVIDENCE:
{json.dumps(evidence, indent=2)}

Produce a clear professional report with these headings:

1. Claim Overview
2. Relevant Policy Evidence
3. Coverage and Exclusion Analysis
4. Rule Assessment Interpretation
5. Missing Information and Risks
6. Recommended Next Steps
7. Human Review Requirements

Reference evidence using its chunk ID and page number.
If no useful evidence was retrieved, clearly disclose that.
"""

    payload = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a cautious insurance evidence analyst. "
                    "Never fabricate evidence or make final claim decisions."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1800,
    }

    request = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ClaimLensAI/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as exc:
        # Do not expose request headers or API credentials.
        raise RuntimeError(
            f"Groq API returned HTTP {exc.code}. "
            "Check API access, model availability and configuration."
        ) from None

    except urllib.error.URLError:
        raise RuntimeError(
            "Could not connect to Groq API. Check your internet connection."
        ) from None

    analysis = result["choices"][0]["message"]["content"]

    return ClaimAIAnalysis(
        claim_id=claim.claim_id,
        policy_id=policy.policy_id,
        rule_assessment=assessment,
        analysis=analysis,
        sources=sources,
        human_review_required=True,
    )
