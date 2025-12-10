import json
from typing import List, Dict, Any
from openai import OpenAI
import textwrap
import re


# ----------------------------------------------------------
# Construct prompt for MCQ generation
# ----------------------------------------------------------
def _build_mcq_prompt(source_text: str, num_questions: int, difficulty: str) -> str:

    # Trim overly long text for cost/performance
    max_chars = 4000
    if len(source_text) > max_chars:
        source_text = source_text[:max_chars]

    difficulty_instructions = {
        "easy": "Use simple vocabulary and direct factual questions.",
        "medium": "Use moderate vocabulary and test key comprehension.",
        "hard": "Use deeper inference and higher-order reasoning.",
    }

    diff_rule = difficulty_instructions.get(
        difficulty.lower(), difficulty_instructions["medium"]
    )

    prompt = f"""
You are an expert education content creator.

Create {num_questions} multiple-choice questions based ONLY on the text below.

RULES:
- Each question MUST have exactly 4 options: A, B, C, D.
- Only ONE option can be correct.
- Make the difficulty level: {difficulty}. {diff_rule}
- Provide a short explanation for the correct answer.
- Return ONLY valid JSON in this format:

[
  {{
    "question": "string",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "answer": "A",
    "explanation": "string"
  }},
  ...
]

TEXT:
\"\"\"
{source_text}
\"\"\"
    """

    return textwrap.dedent(prompt).strip()



# ----------------------------------------------------------
# Generate MCQs using OpenAI
# ----------------------------------------------------------
def generate_mcqs(
    client: OpenAI,
    source_text: str,
    num_questions: int = 5,
    difficulty: str = "medium",
) -> List[Dict[str, Any]]:

    if not source_text or not source_text.strip():
        return []

    prompt = _build_mcq_prompt(source_text, num_questions, difficulty)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": "You generate high-quality MCQs."},
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content

    # Try clean direct JSON parse
    try:
        mcq_list = json.loads(raw)
        if isinstance(mcq_list, list):
            return _normalize_mcqs(mcq_list)
    except Exception:
        pass

    # Attempt to extract JSON array from noisy output
    match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
    if match:
        try:
            mcq_list = json.loads(match.group(0))
            return _normalize_mcqs(mcq_list)
        except Exception:
            return []

    return []


# ----------------------------------------------------------
# Normalize + validate MCQ objects
# ----------------------------------------------------------
def _normalize_mcqs(mcqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    cleaned = []

    for item in mcqs:
        q = str(item.get("question", "")).strip()
        options = item.get("options", [])
        answer = str(item.get("answer", "")).strip().upper()
        explanation = str(item.get("explanation", "")).strip()

        if not q or len(options) != 4:
            continue

        # Fix answer if malformed
        if answer not in ["A", "B", "C", "D"]:
            if len(answer) > 0:
                answer = answer[0]
            if answer not in ["A", "B", "C", "D"]:
                answer = "A"

        cleaned.append(
            {
                "question": q,
                "options": options,
                "answer": answer,
                "explanation": explanation or "This answer is correct based on the passage.",
            }
        )

    return cleaned
