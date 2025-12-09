import streamlit as st
from Helpers.textExtractionHelper import extract_text_from_file
from Helpers.curriculumAgent import call_curriculum_agent
import time
import hashlib
import io


# ----------------------------------------------------
# 🧠 HASH HELPERS (CACHE KEYS)
# ----------------------------------------------------
def hash_bytes(data: bytes):
    """Consistent hash key for caching PDF/TXT contents."""
    return hashlib.sha256(data).hexdigest()


# ----------------------------------------------------
# ⚡ CACHED: TEXT EXTRACTION
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_extract_text(file_hash: str, file_bytes: bytes):
    """
    Extract text from raw bytes (no filename needed).
    Cached using the file hash.
    """
    return extract_text_from_file(file_bytes)


# ----------------------------------------------------
# ⚡ CACHED: AI STRUCTURING
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_structure_text(text_hash: str, raw_text: str):
    """
    Runs LLM structuring on raw curriculum text.
    Cached using text hash.
    """
    return call_curriculum_agent(raw_text)


# ----------------------------------------------------
# 📘 PLANNER TAB (Upload → Extract → Structure)
# ----------------------------------------------------
def plannerTab():

    st.subheader("📘 Curriculum Planner")

    # --------------------------------------------
    # FILE UPLOADER (instant, no delay)
    # --------------------------------------------
    uploaded_file = st.file_uploader(
        "Upload curriculum (PDF / TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=False
    )

    # Optional default file (for demo)
    use_default = st.checkbox("Use sample curriculum", value=False)

    default_text = """Python Mastery Program
Module 1: Python Basics
Skills: syntax, variables, loops
Module 2: Data Structures
Skills: lists, dictionaries, tuples
Module 3: OOP
Skills: classes, inheritance, polymorphism
"""

    # State keys
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)

    # --------------------------------------------
    # HANDLE DEFAULT CURRICULUM (NO DELAY)
    # --------------------------------------------
    if use_default and st.button("Analyze Default Curriculum"):
        raw_text = default_text
        st.session_state["curriculum_text"] = raw_text

        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(
                hash_bytes(raw_text.encode()),
                raw_text
            )
            st.session_state["curriculum_structure"] = structure

        st.success("✨ Curriculum extracted! Scroll down.")
        return  # Skip file processing

    # --------------------------------------------
    # HANDLE UPLOADED FILE
    # --------------------------------------------
    if uploaded_file and st.button("Analyze Curriculum"):

        file_bytes = uploaded_file.read()
        file_hash = hash_bytes(file_bytes)

        # STEP 1 — Extract text (cached)
        with st.spinner("📄 Reading curriculum…"):
            raw_text = cached_extract_text(file_hash, file_bytes)
            st.session_state["curriculum_text"] = raw_text

        # STEP 2 — Structure text (cached)
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(
                hash_bytes(raw_text.encode()),
                raw_text
            )
            st.session_state["curriculum_structure"] = structure

        st.success("✨ Curriculum extracted! Scroll down to explore.")

    # --------------------------------------------
    # RENDER RESULTS
    # --------------------------------------------
    raw_text = st.session_state["curriculum_text"]
    structure = st.session_state["curriculum_structure"]

    # --- RAW TEXT PREVIEW ---
    if raw_text:
        st.subheader("📄 Raw Text Preview")
        st.text(raw_text[:2000])

    # --- STRUCTURED CURRICULUM ---
    if structure:
        st.subheader("📚 Extracted Curriculum Structure")

        st.write(f"**Title:** {structure.get('title', 'Untitled Curriculum')}")

        for i, module in enumerate(structure.get("modules", []), start=1):
            with st.expander(f"📦 Module {i}: {module.get('name','Unnamed Module')}"):

                st.write(module.get("description", "No description available."))

                skills = module.get("skills", [])
                if skills:
                    st.markdown("**🎯 Skills Covered:**")
                    for s in skills:
                        st.write(f"- {s}")
                else:
                    st.info("No skills extracted for this module.")


# ----------------------------------------------------
# 🎓 STREAMLIT PAGE WRAPPER (Tab #3 entry point)
# ----------------------------------------------------
def streamlitPage():
    """
    Lightweight wrapper for Tab #3.
    Keeps UI instant and handles its own internal spinners.
    """

    st.header("🎓 Curriculum Intelligence")

    # Show a fast spinner to avoid blank-screen feeling
    placeholder = st.container()
    with placeholder:
        with st.spinner("Loading curriculum tools…"):
            time.sleep(0.05)

    placeholder.empty()

    plannerTab()
