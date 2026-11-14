import json
from pathlib import Path

from backend.app.schemas.claim import Claim


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CLAIMS_DIRECTORY = PROJECT_ROOT / "data" / "claims"


def load_claims() -> list[Claim]:
    claims = []

    for file_path in sorted(CLAIMS_DIRECTORY.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        claim = Claim.model_validate(raw_data)
        claims.append(claim)

    return claims
