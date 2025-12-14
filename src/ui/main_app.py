import streamlit as st
from dotenv import load_dotenv

from src.services.openai_client import get_openai_client
from src.modules.speaking.ui import evaluate_speaking
from src.modules.book_tutor.ui import ask_the_book_tab
from src.modules.curriculum.ui import streamlit_page
from src.ui.components import footer
from src.ui.sidebar import render_sidebar
from src.modules.MCQ_Generator.mcq_ui import mcq_generator_tab
from src.modules.vocabulary_builder.ui import vocabulary_builder_tab
from src.modules.book_recommendations.ui import book_recommendations_tab
import os

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AI Education Coach",
    page_icon="🐶",
    initial_sidebar_state="expanded",
    layout="wide"
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
def cached_mcq_generator():
    return mcq_generator_tab

@st.cache_resource
def cached_vocabulary_builder():
    return vocabulary_builder_tab

@st.cache_resource
def cached_book_recommendations():
    return book_recommendations_tab

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗣️ Speaking / Practice",
        "📖 Ask The Book",
        "📚 Summarize Curriculum",
        "🎓 MCQ Generator",
        "💡 Vocabulary Builder",
        "📚 Luffy Book Recommendations"
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

    # -----------------------------
    # TAB 4 — MCQ GENERATOR
    # -----------------------------
    with tab4:
        with st.spinner("Loading MCQ Generator…"):
            mcq_generator = cached_mcq_generator()  # only loads once
        mcq_generator(client)

    # -----------------------------
    # TAB 5 — VOCABULARY BUILDER
    # -----------------------------
    with tab5:
        with st.spinner("Loading Vocabulary Builder…"):
            vocabulary_builder = cached_vocabulary_builder()  # only loads once
        vocabulary_builder(client)

    # -----------------------------
    # TAB 6 — BOOK RECOMMENDATIONS
    # -----------------------------
    with tab6:
        with st.spinner("Loading Book Recommendations…"):
            book_recommendations = cached_book_recommendations()  # only loads once
        book_recommendations(client)

# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    main()
    footer()

