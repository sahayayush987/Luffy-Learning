import streamlit as st
import time

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

    uploaded_file = st.file_uploader("Upload curriculum", type=["pdf", "txt"])

    # Init state only (cheap)
    st.session_state.setdefault("curriculum_text", None)
    st.session_state.setdefault("curriculum_structure", None)

    # Display instantly — no slowdown
    preview = st.container()
    structured = st.container()

    # ------------------------------------------------
    # ONLY heavy work runs AFTER click
    # ------------------------------------------------
    if uploaded_file and st.button("Analyze Curriculum", type="primary"):

        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name

        # STEP 1 — Extract
        with st.spinner("📄 Reading curriculum…"):
            text = cached_extract_text(file_bytes, file_name)
            st.session_state.curriculum_text = text

        # STEP 2 — Structure
        with st.spinner("🧠 Understanding curriculum…"):
            structure = cached_structure_text(text)
            st.session_state.curriculum_structure = structure

        st.success("✨ Curriculum extracted! Scroll down.")

    # ------------------------------------------------
    # UI below renders instantly
    # ------------------------------------------------
    if st.session_state.curriculum_text:
        with preview:
            st.subheader("📄 Raw Text Preview")
            st.text(st.session_state.curriculum_text[:2000])

    if st.session_state.curriculum_structure:
        structure = st.session_state.curriculum_structure

        with structured:
            st.subheader("📚 Extracted Curriculum")

            st.write(f"**Title:** {structure.get('title', 'Untitled Curriculum')}")

            for i, mod in enumerate(structure.get("modules", []), 1):
                with st.expander(f"📦 Module {i}: {mod.get('name','Unnamed')}"):
                    st.write(mod.get("description", ""))

                    skills = mod.get("skills", [])
                    if skills:
                        st.markdown("**🎯 Skills:**")
                        for s in skills:
                            st.write(f"- {s}")
                    else:
                        st.info("No skills listed.")


# ----------------------------------------------------
# 🎓 WRAPPER (Tab 3 entry) — **zero delay**
# ----------------------------------------------------
def streamlitPage():
    st.header("🎓 Curriculum Intelligence")
    plannerTab()
