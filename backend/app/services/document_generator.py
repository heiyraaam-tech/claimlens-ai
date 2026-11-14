from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "documents" / "policies"


def generate_policy_pdf() -> Path:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIRECTORY / "policy_001.pdf"

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="PolicyTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        fontSize=20,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="ClauseHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=6,
    ))

    story = []

    story.append(Paragraph("NORTHSTAR INSURANCE", styles["Heading1"]))
    story.append(Paragraph(
        "INDIVIDUAL HEALTH INSURANCE POLICY",
        styles["PolicyTitle"],
    ))
    story.append(Paragraph(
        "Synthetic demonstration document — not a real insurance contract.",
        styles["Italic"],
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("1. Policy Information", styles["ClauseHeading"]))

    policy_data = [
        ["Policy ID", "POL-1001"],
        ["Policyholder", "Alex Morgan"],
        ["Policy Type", "Health Insurance"],
        ["Provider", "NorthStar Insurance"],
        ["Effective Date", "01 January 2026"],
        ["Expiry Date", "31 December 2026"],
        ["Sum Insured", "INR 5,00,000"],
        ["Deductible", "INR 10,000"],
    ]

    table = Table(policy_data, colWidths=[55 * mm, 105 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8EEF5")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)

    story.append(Paragraph("2. Covered Benefits", styles["ClauseHeading"]))
    story.append(Paragraph(
        "Subject to the terms, conditions, limits and exclusions of this "
        "policy, the following benefits are listed as covered:",
        styles["BodyText"],
    ))

    benefits = [
        "Hospitalization",
        "Emergency treatment",
        "Accidental injuries",
        "Surgical procedures",
    ]

    for benefit in benefits:
        story.append(Paragraph(f"• {benefit}", styles["BodyText"]))

    story.append(Paragraph("3. Exclusions", styles["ClauseHeading"]))
    story.append(Paragraph(
        "The following treatments are excluded under this synthetic policy:",
        styles["BodyText"],
    ))

    exclusions = [
        "Cosmetic procedures",
        "Experimental treatments",
        "Self-inflicted injuries",
    ]

    for exclusion in exclusions:
        story.append(Paragraph(f"• {exclusion}", styles["BodyText"]))

    story.append(Paragraph("4. Waiting Period", styles["ClauseHeading"]))
    story.append(Paragraph(
        "A general waiting period of 30 days applies from the policy "
        "effective date. Claims arising from incidents during this period "
        "require assessment under the applicable policy terms.",
        styles["BodyText"],
    ))

    story.append(Paragraph("5. Sum Insured and Deductible", styles["ClauseHeading"]))
    story.append(Paragraph(
        "The maximum sum insured stated in this policy is INR 5,00,000. "
        "A deductible of INR 10,000 applies, subject to the applicable "
        "benefit terms. The actual payable amount requires claim-level "
        "assessment and verification.",
        styles["BodyText"],
    ))

    story.append(Paragraph("6. Claim Assessment", styles["ClauseHeading"]))
    story.append(Paragraph(
        "Every submitted claim is subject to policy verification, "
        "document review, applicable exclusions, waiting periods and "
        "human review. This document does not guarantee claim approval.",
        styles["BodyText"],
    ))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "END OF SYNTHETIC POLICY DOCUMENT",
        styles["Italic"],
    ))

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(20 * mm, 12 * mm, "NorthStar Insurance | Demo")
        canvas.drawRightString(
            A4[0] - 20 * mm,
            12 * mm,
            f"Page {doc.page}",
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return output_path


if __name__ == "__main__":
    generated_file = generate_policy_pdf()
    print(f"Policy PDF generated: {generated_file}")
