import streamlit as st
from Helpers.textExtractionHelper import extract_text_from_file
from Helpers.curriculumAgent import call_curriculum_agent
import time

# ----------------------------------------------------
# ⚡ CACHED: Extract Text (uploaded_file object)
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_extract_text(uploaded_file):
    """
    Extract text from the raw uploaded file.
    Cached so the same file never reprocesses again.
    """
    return extract_text_from_file(uploaded_file)


# ----------------------------------------------------
# ⚡ CACHED: Structure Text (LLM call)
# ----------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_structure_text(raw_text):
    """
    Calls LLM to structure curriculum.
    Cached so re-renders never re-call the model.
    """
    return call_curriculum_agent(raw_text)


# ----------------------------------------------------
# 📘 PLANNER TAB (Upload → Extract → Structure)
# ----------------------------------------------------
def plannerTab():

    uploaded_file = st.file_uploader(
        "Upload curriculum (PDF / TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=False
    )

    # Ensure state keys exist
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)

    preview_container = st.container()
    structure_container = st.container()

    # ----------------------------
    # PROCESS AFTER BUTTON CLICK
    # ----------------------------
    if uploaded_file and st.button("Analyze Curriculum", type="primary"):

        # STEP 1 — Extract Text
        with st.spinner("📄 Reading curriculum…"):
            text = cached_extract_text(uploaded_file)
            st.session_state["curriculum_text"] = text

        # STEP 2 — Structure with AI
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(text)
            st.session_state["curriculum_structure"] = structure

        st.success("✨ Curriculum extracted! Scroll down to explore.")

    # ----------------------------
    # RAW TEXT PREVIEW
    # ----------------------------
    if st.session_state["curriculum_text"]:
        with preview_container:
            st.subheader("📄 Raw Text Preview")
            st.text(st.session_state["curriculum_text"][:2000])

    # ----------------------------
    # STRUCTURED CURRICULUM
    # ----------------------------
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
    Simple wrapper for Tab 3.
    Shows a quick spinner before rendering the Planner.
    """

    st.header("🎓 Curriculum Intelligence")

    placeholder = st.container()
    with placeholder:
        with st.spinner("Loading curriculum tools…"):
            time.sleep(0.1)  # tiny delay so spinner actually appears

    placeholder.empty()

    plannerTab()
