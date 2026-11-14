# ClaimLens AI
### AI-Powered Insurance Claim Intelligence Platform

ClaimLens AI is an AI-assisted insurance claim analysis prototype combining deterministic rules, PDF policy extraction, semantic retrieval, and LLM-powered evidence analysis.

## Features
- FastAPI REST API
- PDF policy extraction with PyMuPDF
- Section-aware document chunking
- Sentence Transformers embeddings
- ChromaDB vector database
- Deterministic insurance rules engine
- Groq-powered evidence-grounded AI analysis
- Human-review safeguards
- Automated Pytest suite

## Tech Stack
Python 3.12, FastAPI, ChromaDB, Sentence Transformers, PyMuPDF, ReportLab, Groq API, Pytest.

## Setup
1. Create a virtual environment:
   `python3.12 -m venv .venv`
2. Activate it:
   `source .venv/bin/activate`
3. Install dependencies:
   `pip install -r backend/requirements.txt`
4. Copy `.env.example` to `.env` and configure your Groq API key.

## Run
`uvicorn backend.app.main:app --reload`

## API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/claims/` | List claims |
| POST | `/api/v1/claims/{claim_id}/assess` | Rules-based assessment |
| POST | `/api/v1/claims/{claim_id}/analyze` | AI-assisted analysis |

## Tests
`python -m pytest -q`

## Limitations
All included policies and claims are synthetic demo data. The rules engine is heuristic, AI output can be incorrect, and similarity scores are ranking signals rather than confidence scores. Final claim decisions require authorized human review. This is a portfolio prototype, not a production insurance adjudication system.
