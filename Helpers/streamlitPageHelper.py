import streamlit as st
from Helpers.textExtractionHelper import extract_text_from_file
from Helpers.curriculumAgent import call_curriculum_agent


# =========================================================
# 🧠 CACHING — Extract Text
# =========================================================
@st.cache_data(show_spinner=False)
def cached_extract_text(file_bytes: bytes, file_name: str):
    """
    Extract raw text from a PDF/TXT file.
    Cached using file bytes & filename hash.
    """
    return extract_text_from_file(file_bytes, file_name)


# =========================================================
# 🧠 CACHING — AI Structuring
# =========================================================
@st.cache_data(show_spinner=False)
def cached_structure_text(raw_text: str):
    """
    Convert raw curriculum text into structured format.
    Cached using text hash.
    """
    return call_curriculum_agent(raw_text)


# =========================================================
# 📘 PLANNER TAB
# =========================================================
def plannerTab():

    st.subheader("📘 Curriculum Planner")

    # ------------------------------
    # File upload (super lightweight)
    # ------------------------------
    uploaded_file = st.file_uploader(
        "Upload curriculum (PDF / TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=False
    )

    # Default file (auto-load option)
    default_path = "Helpers/defaults/python_curriculum_detailed.txt"

    # Create session state once
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)
    st.session_state.setdefault("curriculum_filename", None)

    # ------------------------------
    # PROCESSING: Only when button clicked
    # ------------------------------
    if st.button("Analyze Curriculum", type="primary"):

        # 1️⃣ Determine source (uploaded OR default)
        if uploaded_file:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
        else:
            # Load the default file
            with open(default_path, "rb") as f:
                file_bytes = f.read()
            file_name = "python_curriculum_detailed.txt"

        # Cache filename
        st.session_state.curriculum_filename = file_name

        # 2️⃣ Extract raw text
        with st.spinner("📄 Reading curriculum…"):
            text = cached_extract_text(file_bytes, file_name)
            st.session_state.curriculum_text = text

        # 3️⃣ AI Structuring
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(text)
            st.session_state.curriculum_structure = structure

        st.success("✨ Curriculum extracted! Scroll down.")

    # ========================================================
    # UI RENDERING — ALWAYS INSTANT (no delays)
    # ========================================================

    # RAW TEXT PREVIEW
    if st.session_state.curriculum_text:
        st.subheader("📄 Raw Text Preview")
        st.text(st.session_state.curriculum_text[:2000])

    # STRUCTURED OUTPUT
    structure = st.session_state.curriculum_structure

    if structure:
        st.subheader("📚 Extracted Curriculum Structure")

        # Title
        st.write(f"**Title:** {structure.get('title', 'Untitled Curriculum')}")

        # Modules
        modules = structure.get("modules", [])

        if not modules:
            st.warning("⚠ No modules or skills extracted. Try another file.")
        else:
            for i, mod in enumerate(modules, 1):
                with st.expander(f"📦 Module {i}: {mod.get('name', 'Unnamed Module')}"):

                    st.write(mod.get("description", "No description provided."))

                    skills = mod.get("skills", [])
                    if skills:
                        st.markdown("**🎯 Skills Covered:**")
                        for s in skills:
                            st.write(f"- {s}")
                    else:
                        st.info("No skills listed for this module.")


# =========================================================
# 🎓 MAIN PAGE WRAPPER FOR TAB 3
# =========================================================
def streamlitPage():
    """
    Super lightweight wrapper used by the main app.
    Does NOT do heavy work — plannerTab() handles everything.
    """

    st.header("🎓 Curriculum Intelligence")
    st.caption("Upload or auto-load a curriculum and let AI organize it for you.")

    # This loads instantly — all heavy work is in spinners
    plannerTab()
