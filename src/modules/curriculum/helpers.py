import re
from pypdf import PdfReader


# ============================================================
# 🧼 TEXT CLEANING UTILITIES
# ============================================================

def detect_bullet_points(text: str) -> str:
    """
    Convert lines that look like lists into proper bullet points.
    """
    lines = text.split("\n")
    output = []

    for line in lines:
        stripped = line.strip()

        # Matches things like:
        # - item
        # • item
        # 1. item
        # * item
        if re.match(r"^(\d+\.\s+|[-•–*]\s+)", stripped):
            cleaned_item = re.sub(r"^(\d+\.\s+|[-•–*]\s+)", "", stripped)
            output.append(f"• {cleaned_item}")
        else:
            output.append(stripped)

    return "\n".join(output)


def clean_pdf_text(text: str) -> str:
    """
    Cleans raw PDF text into readable paragraphs with basic structure.
    Improves formatting for curriculum-like documents.
    """

    # -----------------------------------------------------------
    # 1️⃣ Fix broken hyphenation
    # -----------------------------------------------------------
    text = re.sub(r"-\s*\n", "", text)

    # -----------------------------------------------------------
    # 2️⃣ Merge mid-sentence line breaks
    # -----------------------------------------------------------
    text = re.sub(r"(?<![.!?])\n(?!\n)", " ", text)

    # -----------------------------------------------------------
    # 3️⃣ Remove extra spaces & normalize newlines
    # -----------------------------------------------------------
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # -----------------------------------------------------------
    # 4️⃣ Convert likely section headers into Markdown headings
    # -----------------------------------------------------------
    def header_format(m):
        header = m.group(1).strip()
        return f"\n\n### {header}\n\n"

    text = re.sub(
        r"\n([A-Z][A-Za-z ]{1,40})\n",  # short capitalized line
        header_format,
        text
    )

    # -----------------------------------------------------------
    # 5️⃣ Break paragraphs by sentence boundaries
    # -----------------------------------------------------------
    text = re.sub(
        r"(?<=[.!?])\s+(?=[A-Z])",
        "\n\n",
        text
    )

    # -----------------------------------------------------------
    # 6️⃣ Bullet point reconstruction
    # -----------------------------------------------------------
    text = detect_bullet_points(text)

    return text.strip()


# ============================================================
# 📘 PDF → CLEAN TEXT EXTRACTION
# ============================================================

def extract_text_from_file(uploaded_file):
    """
    Extracts text from a PDF or raw TXT file and returns cleaned output.
    """

    # TXT passthrough
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    # PDF handling
    pdf = PdfReader(uploaded_file)

    raw_text = ""
    for i, page in enumerate(pdf.pages):
        if i > 10:  # Safety limit — adjust as needed
            break
        page_text = page.extract_text() or ""
        raw_text += page_text + "\n\n"

    cleaned = clean_pdf_text(raw_text)
    return cleaned


# ============================================================
# 🤖 SUMMARY + TABLE OF CONTENTS GENERATOR
# ============================================================

def generate_curriculum_summary(client, cleaned_text: str) -> str:
    """
    Splits curriculum into sections, generates GPT summaries,
    and builds a table of contents with anchor links.
    """

    # Extract sections based on ### headers
    sections = re.split(r"### ", cleaned_text)
    sections = [s.strip() for s in sections if s.strip()]
    structured_output = []
    toc_entries = []

    for section in sections:
        # Split header title from section content
        parts = section.split("\n", 1)

        header = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ""

        anchor = header.lower().replace(" ", "-")
        toc_entries.append(f"- [{header}](#{anchor})")

        # Generate summary
        prompt = f"""
        Summarize the following curriculum section into 2–3 clear,
        parent-friendly sentences. Keep all meaning accurate.

        Section Title: {header}

        Section Text:
        {content}
        """

        try:
            summary = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
        except Exception as e:
            summary = "(Summary unavailable due to an error.)"

        formatted = (
            f"<a name='{anchor}'></a>\n"
            f"### {header}\n\n"
            f"**Summary:** {summary}\n\n"
            f"{content}\n\n"
        )

        structured_output.append(formatted)

    # Build final curriculum document
    final_doc = (
        "## Table of Contents\n\n"
        + "\n".join(toc_entries)
        + "\n\n---\n\n"
        + "\n\n---\n\n".join(structured_output)
    )

    return final_doc
