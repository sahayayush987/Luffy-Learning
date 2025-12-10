import json
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()  

def call_curriculum_agent(raw_text: str) -> dict:
    """
    Uses an LLM to convert a text curriculum into structured JSON format.
    """
    if not raw_text.strip():
        st.warning("No text to process.")
        return {}

    system_prompt = """
You are CurricAI, an expert curriculum architect.

Extract a JSON structure from the provided syllabus or curriculum:
{
  "title": "Course title",
  "modules": [
    {
      "name": "Module name",
      "description": "1-2 sentence description",
      "skills": [
        "Action-based skill 1",
        "Action-based skill 2"
      ]
    }
  ]
}

Rules:
- Keep JSON clean and valid.
- Max 12 modules unless clearly needed.
- Skills MUST start with verbs: Explain, Build, Design, Analyze, Implement, etc.
- No commentary or markdown outside JSON.
"""

    # Avoid too-long tokens for now
    trimmed_text = raw_text[:15000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": trimmed_text},
        ],
        temperature=0.3
    )

    result = response.choices[0].message.content

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        st.error("Failed to parse JSON. Displaying raw output.")
        return {"raw_output": result}


def generate_tasks_from_structure(structure: dict) -> list:
    """
    Generate simple learning tasks from each skill in the curriculum structure.
    """
    tasks = []

    if not structure or "modules" not in structure:
        return tasks

    for module in structure["modules"]:
        module_name = module.get("name", "Module")
        for skill in module.get("skills", []):
            task = f"[{module_name}] Practice: {skill}"
            tasks.append(task)

    return tasks

