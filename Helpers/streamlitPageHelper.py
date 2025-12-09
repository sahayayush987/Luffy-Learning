import streamlit as st
from Helpers.textExtractionHelper import extract_text_from_file
from Helpers.curriculumAgent import call_curriculum_agent


# ================================================
# 🧠 CACHE: Extract raw text (bytes + filename)
# ================================================
@st.cache_data(show_spinner=False)
def cached_extract_text(file_bytes: bytes, file_name: str):
    """Extract raw text from uploaded or default curriculum file."""
    return extract_text_from_file(file_bytes, file_name)


# ================================================
# 🧠 CACHE: AI structure
# ================================================
@st.cache_data(show_spinner=False)
def cached_structure_text(raw_text: str):
    """Convert curriculum text into structured modules."""
    return call_curriculum_agent(raw_text)


# ================================================
# 📘 MAIN CURRICULUM LOGIC
# ================================================
def plannerTab():

    st.subheader("📘 Curriculum Planner")

    uploaded_file = st.file_uploader(
        "Upload curriculum (PDF / TXT)", 
        type=["pdf", "txt"]
    )

    # Init state
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)

    # -------------------------------
    # 🔥 PROCESS ONLY ON BUTTON CLICK
    # -------------------------------
    if st.button("Analyze Curriculum", type="primary"):

        # Default file fallback
        default_path = "Helpers/defaults/python_curriculum_detailed.txt"

        if uploaded_file:
            file_bytes = uploaded_file.read()   # <-- ALWAYS bytes
            file_name = uploaded_file.name
        else:
            with open(default_path, "rb") as f:
                file_bytes = f.read()
            file_name = "python_curriculum_detailed.txt"

        # STEP 1 — Extract text
        with st.spinner("📄 Reading curriculum…"):
            text = cached_extract_text(file_bytes, file_name)
            st.session_state.curriculum_text = str(text)   # <-- ALWAYS cast to string

        # STEP 2 — AI structuring
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(st.session_state.curriculum_text)
            st.session_state.curriculum_structure = structure

        st.success("✨ Curriculum extracted successfully! Scroll down.")

    # ------------------------------------------------
    # 📄 TEXT PREVIEW (always safe)
    # ------------------------------------------------
    text = st.session_state.curriculum_text
    if isinstance(text, str) and len(text) > 0:
        st.subheader("📄 Raw Text Preview")
        st.text(text[:2000])

    # ------------------------------------------------
    # 📚 STRUCTURED OUTPUT
    # ------------------------------------------------
    structure = st.session_state.curriculum_structure
    if isinstance(structure, dict):
        st.subheader("📚 Extracted Curriculum Structure")
        st.write(f"**Title:** {structure.get('title', 'Untitled Curriculum')}")

        modules = structure.get("modules", [])

        if not modules:
            st.warning("⚠ No modules or skills extracted. Try another file.")
        else:
            for i, module in enumerate(modules, 1):

                with st.expander(f"📦 Module {i}: {module.get('name', 'Unnamed Module')}"):

                    st.write(module.get("description", "No description provided."))

                    skills = module.get("skills", [])
                    if skills:
                        st.markdown("**🎯 Skills Covered:**")
                        for skill in skills:
                            st.write(f"- {skill}")
                    else:
                        st.info("No skills listed for this module.")


# ================================================
# 🎓 WRAPPER CALLED FROM MAIN APP
# ================================================
def streamlitPage():
    st.header("🎓 Curriculum Intelligence")
    plannerTab()
