import streamlit as st
import time
import os

# ----------------------------------------------------
# ✨ Lazy import wrappers (ONLY run after button click)
# ----------------------------------------------------
def extract_text_lazy(file_bytes, file_name):
    # Import inside click only (never during tab load)
    from Helpers.textExtractionHelper import extract_text_from_file
    return extract_text_from_file(file_bytes, file_name)

def structure_text_lazy(text):
    from Helpers.curriculumAgent import call_curriculum_agent
    return call_curriculum_agent(text)


# ----------------------------------------------------
# ⚡ CACHING (initialized ONLY on first use)
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_extract_text(file_bytes, file_name):
    return extract_text_lazy(file_bytes, file_name)

@st.cache_data(show_spinner=False)
def cached_structure_text(raw_text):
    return structure_text_lazy(raw_text)


# ----------------------------------------------------
# 📘 PLANNER TAB (Instant load)
# ----------------------------------------------------
def plannerTab():

    # -----------------------------
    # Default curriculum file path
    # -----------------------------
    DEFAULT_FILE_PATH = "python_curriculum_detailed.txt"

    # Let user choose data source
    source = st.radio(
        "Select curriculum source:",
        ["Use default Python curriculum", "Upload your own"],
        horizontal=True
    )

    uploaded_file = None

    # -----------------------------
    # Option 1: Use default file
    # -----------------------------
    if source == "Use default Python curriculum":

        if not os.path.exists(DEFAULT_FILE_PATH):
            st.error(f"Default curriculum missing: {DEFAULT_FILE_PATH}")
            return

        st.info("Using default: **School Stuff We Pretend Is Fun 2025**")

        with open(DEFAULT_FILE_PATH, "rb") as f:
            uploaded_file = f.read()              # file bytes
            default_name = os.path.basename(DEFAULT_FILE_PATH)

    # -----------------------------
    # Option 2: Upload user file
    # -----------------------------
    else:
        file = st.file_uploader("Upload curriculum", type=["pdf", "txt"])
        if file:
            uploaded_file = file.getvalue()
            default_name = file.name
        else:
            st.stop()  # user has not uploaded yet → stop rendering below

    # -----------------------------
    # Init session keys
    # -----------------------------
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)

    preview_container = st.container()
    structure_container = st.container()

    # -----------------------------
    # PROCESS CURRICULUM (ONLY WHEN BUTTON IS CLICKED)
    # -----------------------------
    if st.button("Analyze Curriculum", type="primary"):

        # STEP 1 — Extract raw text
        with st.spinner("📄 Reading curriculum…"):
            text = cached_extract_text(uploaded_file, default_name)
            st.session_state.curriculum_text = text

        # STEP 2 — Structure with AI
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(text)
            st.session_state.curriculum_structure = structure

        st.success("✨ Curriculum extracted successfully! Scroll down.")

    # -----------------------------
    # RAW TEXT PREVIEW
    # -----------------------------
    if st.session_state.curriculum_text:
        with preview_container:
            st.subheader("📄 Raw Text Preview")
            st.text(st.session_state.curriculum_text[:2000])

    # -----------------------------
    # STRUCTURED CURRICULUM
    # -----------------------------
    structure = st.session_state.curriculum_structure

    if structure:
        with structure_container:

            st.subheader("📚 Extracted Curriculum Structure")
            st.write(f"**Title:** {structure.get('title', 'Untitled Curriculum')}")

            for i, module in enumerate(structure.get("modules", []), start=1):
                with st.expander(f"📦 Module {i}: {module.get('name','Unnamed Module')}"):

                    st.write(module.get("description", "No description provided."))

                    skills = module.get("skills", [])
                    if skills:
                        st.markdown("**🎯 Skills Covered:**")
                        for skill in skills:
                            st.write(f"- {skill}")
                    else:
                        st.info("No skills listed for this module.")



def streamlitPage():
    st.header("🎓 Curriculum Intelligence")
    with st.spinner("Loading Modules..."):
        plannerTab()
