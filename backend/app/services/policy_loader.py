import json
from pathlib import Path

from backend.app.schemas.policy import Policy


PROJECT_ROOT = Path(__file__).resolve().parents[3]
POLICIES_DIRECTORY = PROJECT_ROOT / "data" / "policies"


def load_policies() -> list[Policy]:
    policies = []

    for file_path in sorted(POLICIES_DIRECTORY.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        policy = Policy.model_validate(raw_data)
        policies.append(policy)

    return policies