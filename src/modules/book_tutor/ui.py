import os
import streamlit as st
from src.modules.book_tutor.tutor import ReadingTutor


# ===================================================================
# 📘 STREAMLIT UI WRAPPER
# ===================================================================

def ask_the_book_tab(client):

    st.subheader("📖 Ask The Book — AI Reading Tutor")

    # Get project root (go up 4 levels from src/modules/book_tutor/ui.py)
    # __file__ -> src/modules/book_tutor/ui.py
    # dirname 1 -> src/modules/book_tutor/
    # dirname 2 -> src/modules/
    # dirname 3 -> src/
    # dirname 4 -> project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    book_options = {
        "The Lost Symbol": "the_lost_symbol.pdf",
        "Halo - The Fall Of Reach": "Halo - The Fall Of Reach.pdf",
    }

    selected = st.selectbox("Choose a book:", list(book_options.keys()))
    tutor_key = f"tutor_{selected}"

    if tutor_key not in st.session_state:
        with st.spinner("Loading book…"):
            st.session_state[tutor_key] = ReadingTutor(
                pdf_name=book_options[selected],
                root_path=project_root
            )

    tutor = st.session_state[tutor_key]

    if not tutor.pdf_loaded:
        st.error(f"PDF not found: {tutor.pdf_path}")
        return

    question = st.text_input("Ask a question about the story:")

    if st.button("Ask"):
        with st.spinner("Thinking…"):
            reply, score = tutor.tutor_turn(question)

        st.markdown(f"**Tutor:** {reply}")

        audio = tutor.speak(reply)
        if audio:
            st.audio(audio, format="audio/mp3")

