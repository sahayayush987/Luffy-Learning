import json
from typing import List, Dict, Any
from openai import OpenAI
import textwrap
import re


# ----------------------------------------------------------
# Construct prompt for vocabulary generation
# ----------------------------------------------------------
def _build_vocabulary_prompt(grade: str, difficulty: str, num_words: int = 10) -> str:
    """
    Build a prompt for generating vocabulary words based on grade and difficulty.
    """
    
    # Grade-specific guidance
    grade_guidance = {
        "1-3": "Elementary level words appropriate for grades 1-3. Focus on basic, commonly used words.",
        "4-6": "Intermediate level words appropriate for grades 4-6. Include more descriptive and academic terms.",
        "7-9": "Middle school level words appropriate for grades 7-9. Include more sophisticated vocabulary.",
        "10-12": "High school level words appropriate for grades 10-12. Include advanced academic and literary vocabulary.",
    }
    
    # Difficulty-specific guidance
    difficulty_instructions = {
        "easy": "Use simpler words that are age-appropriate but still challenging. Focus on common words students should know.",
        "medium": "Use moderately challenging words that expand vocabulary. Include words students may encounter in reading.",
        "hard": "Use advanced words that are challenging and expand vocabulary significantly. Include sophisticated and academic terms.",
    }
    
    grade_rule = grade_guidance.get(grade, grade_guidance["4-6"])
    diff_rule = difficulty_instructions.get(
        difficulty.lower(), difficulty_instructions["medium"]
    )
    
    prompt = f"""
You are an expert vocabulary educator.

Generate exactly {num_words} vocabulary words appropriate for {grade} grade level with {difficulty} difficulty.

RULES:
- Each word MUST include: word, part of speech, definition, example sentence, and synonyms (if applicable).
- Grade level: {grade_rule}
- Difficulty: {diff_rule}
- Make sure words are age-appropriate and educational.
- Provide clear, concise definitions that students can understand.
- Example sentences should be clear and demonstrate proper usage.
- Return ONLY valid JSON in this format:

[
  {{
    "word": "string",
    "part_of_speech": "string (noun, verb, adjective, adverb, etc.)",
    "definition": "string",
    "example_sentence": "string",
    "synonyms": ["string1", "string2"]  // optional, can be empty array
  }},
  ...
]

Generate exactly {num_words} words. Do not include any text outside the JSON array.
    """
    
    return textwrap.dedent(prompt).strip()


# ----------------------------------------------------------
# Generate vocabulary words using OpenAI
# ----------------------------------------------------------
def generate_vocabulary(
    client: OpenAI,
    grade: str = "4-6",
    difficulty: str = "medium",
    num_words: int = 10,
) -> List[Dict[str, Any]]:
    """
    Generate vocabulary words based on grade and difficulty level.
    
    Args:
        client: OpenAI client instance
        grade: Grade level (e.g., "1-3", "4-6", "7-9", "10-12")
        difficulty: Difficulty level ("easy", "medium", "hard")
        num_words: Number of words to generate (default: 10)
    
    Returns:
        List of dictionaries containing word information
    """
    
    prompt = _build_vocabulary_prompt(grade, difficulty, num_words)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are an expert vocabulary educator who generates age-appropriate vocabulary words with clear explanations."},
            {"role": "user", "content": prompt},
        ],
    )
    
    raw = response.choices[0].message.content
    
    # Try clean direct JSON parse
    try:
        vocab_list = json.loads(raw)
        if isinstance(vocab_list, list):
            return _normalize_vocabulary(vocab_list)
    except Exception:
        pass
    
    # Attempt to extract JSON array from noisy output
    match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
    if match:
        try:
            vocab_list = json.loads(match.group(0))
            return _normalize_vocabulary(vocab_list)
        except Exception:
            return []
    
    return []


# ----------------------------------------------------------
# Normalize + validate vocabulary objects
# ----------------------------------------------------------
def _normalize_vocabulary(vocab: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize and validate vocabulary word objects.
    """
    
    cleaned = []
    
    for item in vocab:
        word = str(item.get("word", "")).strip()
        part_of_speech = str(item.get("part_of_speech", "")).strip()
        definition = str(item.get("definition", "")).strip()
        example_sentence = str(item.get("example_sentence", "")).strip()
        synonyms = item.get("synonyms", [])
        
        if not word or not definition:
            continue
        
        # Ensure synonyms is a list
        if not isinstance(synonyms, list):
            synonyms = []
        
        cleaned.append(
            {
                "word": word,
                "part_of_speech": part_of_speech or "unknown",
                "definition": definition,
                "example_sentence": example_sentence or f"Example: The word '{word}' is used in context.",
                "synonyms": [str(s).strip() for s in synonyms if s],
            }
        )
    
    return cleaned

