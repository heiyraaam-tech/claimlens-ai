from pathlib import Path
import re


SECTION_PATTERN = re.compile(r"^\s*\d+\.\s+\S")


def _split_section(
    section: list[str],
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """Split an oversized section while retaining its heading and context."""

    heading = section[0] if SECTION_PATTERN.match(section[0]) else ""
    body = "\n".join(section[1:] if heading else section).strip()
    prefix = f"{heading}\n" if heading else ""

    available = chunk_size - len(prefix)

    if available <= 0:
        raise ValueError("Section heading exceeds chunk_size")

    if not body:
        return [heading] if heading else []

    if len(prefix) + len(body) <= chunk_size:
        return [prefix + body]

    results = []
    start = 0

    while start < len(body):
        end = min(start + available, len(body))

        if end < len(body):
            boundary = max(
                body.rfind("\n", start, end),
                body.rfind(" ", start, end),
            )
            if boundary > start:
                end = boundary

        part = body[start:end].strip()

        if part:
            results.append(prefix + part)

        if end >= len(body):
            break

        next_start = max(start + 1, end - overlap)

        while next_start < end and body[next_start].isalnum():
            next_start += 1

        start = next_start

    return results


def chunk_pages(
    pages: list[dict],
    source: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict]:
    """
    Create section-aware chunks without merging distinct numbered sections.
    Preserve source filename and original page numbers.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks = []
    source_name = Path(source).name
    source_stem = Path(source_name).stem

    for page in pages:
        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        sections = []
        preamble = []
        current_section = []

        for line in lines:
            if SECTION_PATTERN.match(line):
                if current_section:
                    sections.append(current_section)

                current_section = [line]

            elif current_section:
                current_section.append(line)

            else:
                preamble.append(line)

        if current_section:
            sections.append(current_section)

        # Attach introductory text to the first numbered section.
        if sections and preamble:
            sections[0] = preamble + sections[0]

        elif preamble:
            # Preserve non-section content if it contains useful text.
            useful_text = "\n".join(preamble).strip()

            if useful_text and "END OF SYNTHETIC POLICY DOCUMENT" not in useful_text:
                sections.append(preamble)

        chunk_number = 0

        for section in sections:
            section_chunks = _split_section(
                section,
                chunk_size,
                overlap,
            )

            for chunk_text in section_chunks:
                if not chunk_text.strip():
                    continue

                chunk_number += 1

                heading_match = next(
                    (
                        line for line in chunk_text.splitlines()
                        if SECTION_PATTERN.match(line)
                    ),
                    None,
                )

                chunks.append({
                    "chunk_id": (
                        f"{source_stem}_p{page['page_number']}_c{chunk_number}"
                    ),
                    "text": chunk_text,
                    "metadata": {
                        "source": source_name,
                        "page_number": page["page_number"],
                        "chunk_number": chunk_number,
                    },
                })

    return chunks


if __name__ == "__main__":
    from backend.app.services.pdf_extractor import extract_pdf_pages

    pdf_path = "data/documents/policies/policy_001.pdf"
    pages = extract_pdf_pages(pdf_path)
    chunks = chunk_pages(pages, source=pdf_path)

    print(f"Pages processed: {len(pages)}")
    print(f"Chunks created: {len(chunks)}")

    for chunk in chunks:
        print("\n" + "=" * 70)
        print("Chunk ID:", chunk["chunk_id"])
        print("Metadata:", chunk["metadata"])
        print("Characters:", len(chunk["text"]))
        print("\nText:\n", chunk["text"])
