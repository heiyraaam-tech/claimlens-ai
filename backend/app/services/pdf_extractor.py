from pathlib import Path

import pymupdf as fitz


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def extract_pdf_pages(pdf_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF, preserving individual page numbers.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.is_absolute():
        pdf_path = PROJECT_ROOT / pdf_path

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    extracted_pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            extracted_pages.append({
                "page_number": page_number,
                "text": text,
                "character_count": len(text),
            })

    return extracted_pages


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Combine extracted page text into one string."""
    pages = extract_pdf_pages(pdf_path)

    return "\n\n".join(
        page["text"] for page in pages
    )


if __name__ == "__main__":
    pdf_path = "data/documents/policies/policy_001.pdf"

    pages = extract_pdf_pages(pdf_path)

    print(f"Total pages extracted: {len(pages)}")

    for page in pages:
        print(f"\n--- Page {page['page_number']} ---")
        print(f"Characters: {page['character_count']}")
        print(page["text"][:1000])
