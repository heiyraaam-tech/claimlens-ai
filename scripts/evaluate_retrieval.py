import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.retrieval_evaluator import evaluate_dataset

dataset_path = PROJECT_ROOT / "data" / "evaluation" / "retrieval_questions.json"
report_path = PROJECT_ROOT / "data" / "evaluation" / "latest_results.json"

report = evaluate_dataset(dataset_path, k=3)
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("\n========== CLAIMLENS AI: RETRIEVAL EVALUATION ==========")
for metric, value in report["summary"].items():
    if isinstance(value, float):
        print(f"{metric:32s}: {value:.4f} ({value * 100:.2f}%)")
    else:
        print(f"{metric:32s}: {value}")

failed = [
    item for item in report["results"]
    if not item["hit"]
]

print(f"\nQuestions with no relevant result in top 3: {len(failed)}")
for item in failed:
    print(f"  {item['id']}: {item['question']}")

print(f"\nDetailed report saved to: {report_path.relative_to(PROJECT_ROOT)}")
