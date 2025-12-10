import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from Helpers.streamlitPageHelper import streamlitPage  # Curriculum UI

import os

# API_KEY = st.secrets["OPENAI_API_KEY"]

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="AI Education Coach", layout="centered")
load_dotenv()


# --------------------------------------------------
# CACHE OPENAI CLIENT
# --------------------------------------------------
@st.cache_resource
def get_client():
    return OpenAI()

client = get_client()


# --------------------------------------------------
# MODULE LOADERS (JUST RETURN UI FUNCS)
# --------------------------------------------------
def get_speaking_ui():
    from speaking_practice import evaluate_speaking
    return evaluate_speaking

def get_book_ui():
    from ask_the_book import ask_the_book_tab
    return ask_the_book_tab


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
def footer():
    st.markdown(
        """
        <hr>
        <div style='text-align:center; color:gray; font-size:14px; margin-top:20px;'>
            Built with ❤️ by Luffy Learning • Powered by OpenAI
        </div>
        """,
        unsafe_allow_html=True,
    )

@st.cache_resource
def cached_speaking_ui():
    return get_speaking_ui()

@st.cache_resource
def cached_book_ui():
    return get_book_ui()

@st.cache_resource
def cached_curriculum_page():
    # streamlitPage() does not return a function → 
    # we wrap it in a callable and return THAT
    def wrapper():
        streamlitPage()  
    return wrapper

# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
def main():
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

        # streamlitPage has its own internal spinners for heavy work
        curriculum_ui()



# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    main()
    footer()
