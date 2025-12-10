import streamlit as st
from dotenv import load_dotenv

from src.services.openai_client import get_openai_client
from src.modules.speaking.ui import evaluate_speaking
from src.modules.book_tutor.ui import ask_the_book_tab
from src.modules.curriculum.ui import streamlit_page
from src.ui.components import footer
from src.ui.sidebar import render_sidebar

import os

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Education Coach",
    page_icon="🐶",
    initial_sidebar_state="expanded"
)
load_dotenv()


# --------------------------------------------------
# CACHE OPENAI CLIENT
# --------------------------------------------------
client = get_openai_client()


# --------------------------------------------------
# MODULE LOADERS (JUST RETURN UI FUNCS)
# --------------------------------------------------
@st.cache_resource
def cached_speaking_ui():
    return evaluate_speaking

@st.cache_resource
def cached_book_ui():
    return ask_the_book_tab

@st.cache_resource
def cached_curriculum_page():
    # streamlit_page() does not return a function → 
    # we wrap it in a callable and return THAT
    def wrapper():
        streamlit_page()  
    return wrapper


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
def main():
    # Render sidebar
    render_sidebar()
    
    st.title("🐶 Luffy Learning – AI Education Coach")

    tab1, tab2, tab3 = st.tabs([
        "🗣️ Speaking / Practice",
        "📖 Ask The Book",
        "📚 Summarize Curriculum"
    ])

    # -----------------------------
    # TAB 1 — SPEAKING
    # -----------------------------
    with tab1:
        with st.spinner("Loading Speaking Module…"):
            speaking_ui = cached_speaking_ui()  # only loads once
        speaking_ui(client)

    # -----------------------------
    # TAB 2 — ASK THE BOOK
    # -----------------------------
    with tab2:
        with st.spinner("Loading Book Tutor…"):
            book_ui = cached_book_ui()  # only loads once
        book_ui(client)

    # -----------------------------
    # TAB 3 — CURRICULUM
    # -----------------------------
    with tab3:
        with st.spinner("Loading Curriculum Tools…"):
            curriculum_ui = cached_curriculum_page()  # only loads once

        # streamlit_page has its own internal spinners for heavy work
        curriculum_ui()


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    main()
    footer()

