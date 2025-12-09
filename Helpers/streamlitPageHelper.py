import streamlit as st
from Helpers.textExtractionHelper import extract_text_from_file
from Helpers.curriculumAgent import call_curriculum_agent
import time
import os


# ----------------------------------------------------
# ⚡ CACHED: Extract Text (uploaded_file OR sample text)
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_extract_text_from_upload(uploaded_file):
    """Extract text from an uploaded file."""
    return extract_text_from_file(uploaded_file)


@st.cache_data(show_spinner=False)
def cached_extract_text_from_sample(sample_path):
    """Read text from a bundled curriculum sample."""
    with open(sample_path, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------------------------------
# ⚡ CACHED: Structure Text (LLM call)
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_structure_text(raw_text):
    """LLM structuring — cached."""
    return call_curriculum_agent(raw_text)


# ----------------------------------------------------
# 📘 PLANNER TAB
# ----------------------------------------------------
def plannerTab():

    # -----------------------------------------------
    # SAMPLE CURRICULUM OPTION
    # -----------------------------------------------
    use_sample = st.checkbox("Use sample Python curriculum instead")

    sample_path = "python_curriculum_detailed.txt"

    uploaded_file = None

    if not use_sample:
        uploaded_file = st.file_uploader(
            "Upload curriculum (PDF / TXT)",
            type=["pdf", "txt"]
        )

    # -----------------------------------------------
    # INIT SESSION STATE
    # -----------------------------------------------
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)
    st.session_state.setdefault("curriculum_source", None)

    preview_container = st.container()
    structure_container = st.container()

    # -----------------------------------------------
    # PROCESS BUTTON
    # -----------------------------------------------
    if (uploaded_file or use_sample) and st.button("Analyze Curriculum", type="primary"):

        # OPTION A — SAMPLE
        if use_sample:
            with st.spinner("📄 Loading sample curriculum…"):
                text = cached_extract_text_from_sample(sample_path)
                st.session_state["curriculum_text"] = text
                st.session_state["curriculum_source"] = "sample"

        # OPTION B — UPLOADED FILE
        else:
            with st.spinner("📄 Reading curriculum…"):
                text = cached_extract_text_from_upload(uploaded_file)
                st.session_state["curriculum_text"] = text
                st.session_state["curriculum_source"] = uploaded_file.name

        # STRUCTURE USING AI
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(text)
            st.session_state["curriculum_structure"] = structure

        st.success("✨ Curriculum extracted successfully! Scroll down to explore.")

    # -----------------------------------------------
    # RAW TEXT PREVIEW
    # -----------------------------------------------
    if st.session_state["curriculum_text"]:
        with preview_container:
            source = st.session_state["curriculum_source"]
            st.subheader(f"📄 Raw Text Preview ({source})")
            st.text(st.session_state["curriculum_text"][:2000])

    # -----------------------------------------------
    # STRUCTURED OUTPUT
    # -----------------------------------------------
    structure = st.session_state["curriculum_structure"]

    if structure:
        with structure_container:
            st.subheader("📚 Extracted Curriculum Structure")
            st.write(f"**Title:** {structure.get('title', 'Untitled Curriculum')}")

            modules = structure.get("modules", [])

            if not modules:
                st.warning("⚠ No modules or skills extracted. Try another file.")
            else:
                for i, module in enumerate(modules, start=1):
                    with st.expander(f"📦 Module {i}: {module.get('name', 'Unnamed Module')}"):

                        st.write(module.get("description", "No description provided."))

                        skills = module.get("skills", [])
                        if skills:
                            st.markdown("**🎯 Skills Covered:**")
                            for skill in skills:
                                st.write(f"- {skill}")
                        else:
                            st.info("No skills listed for this module.")


# ----------------------------------------------------
# 🎓 PAGE WRAPPER (Tab 3)
# ----------------------------------------------------
def streamlitPage():
    """
    Lightweight wrapper to avoid UI lag when this tab is opened.
    """

    st.header("🎓 Curriculum Intelligence")

    placeholder = st.container()
    with placeholder:
        with st.spinner("Loading curriculum tools…"):
            time.sleep(0.08)  # small delay so spinner appears

    placeholder.empty()
    plannerTab()
