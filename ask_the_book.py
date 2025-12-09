import os
import time
import sqlite3
import streamlit as st

from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ingestion.vectorStore import vectorStore
from responseCheck import responseCheck
from textToSpeech import TextToSpeech


# ===================================================================
# ⚡ GLOBAL CACHED RESOURCES
# ===================================================================

@st.cache_resource
def get_openai_client():
    return OpenAI()

@st.cache_resource
def get_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

@st.cache_resource
def get_embeddings():
    return OpenAIEmbeddings()

@st.cache_resource
def load_vectorstore_cached(pdf_path: str, chroma_path: str):
    """
    Loads OR reuses a Chroma vectorstore for the given PDF.
    Huge performance win.
    """
    return vectorStore.get_vectorstore(
        pdf_path=pdf_path,
        base_chroma_dir=chroma_path
    )


# ===================================================================
# 📚 READING TUTOR CLASS
# ===================================================================

class ReadingTutor:

    PROMPT = """
You are a safe, friendly, knowledgeable reading tutor.

CRITICAL RULES:
1. Answer ONLY using the Passage shown below.
2. If the answer is in the passage → explain simply.
3. If not enough information → say:
   "I'm not sure from this part of the book."
4. If the passage has unsafe content → say:
   "That part of the story isn't for our age group."
5. Always be positive.

AFTER your answer, ALWAYS add:
• One encouraging phrase 💚
• One small helpful hint
• One follow-up question

---------------------

📘 Passage:
{passage}

❓ Student Question:
{question}

Now answer following ALL rules.
"""

    # -----------------------------------------------------------
    def __init__(self, pdf_name: str, root_path: str):

        self.client = get_openai_client()
        self.llm = get_llm()
        self.embeddings = get_embeddings()

        self._setup_db()

        # absolute PDF path
        self.pdf_path = os.path.join(root_path, "novels", pdf_name)
        chroma_path = os.path.join(root_path, "chroma_stores")

        if not os.path.exists(self.pdf_path):
            self.db = None
            self.pdf_loaded = False
            return

        try:
            self.db = load_vectorstore_cached(self.pdf_path, chroma_path)
            self.pdf_loaded = True
        except Exception as e:
            print("Vectorstore load error:", e)
            self.db = None
            self.pdf_loaded = False

    # -----------------------------------------------------------
    def _setup_db(self):
        self.conn = sqlite3.connect("feedback.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                timestamp REAL,
                event TEXT,
                passage TEXT,
                question TEXT,
                score REAL,
                latency REAL
            )
            """
        )
        self.conn.commit()

    # -----------------------------------------------------------
    def _log(self, event, passage, question, score, start_time):
        latency = time.time() - start_time
        self.cursor.execute(
            "INSERT INTO logs VALUES (?,?,?,?,?,?)",
            (time.time(), event, passage, question, score, latency),
        )
        self.conn.commit()

    # -----------------------------------------------------------
    def tutor_turn(self, student_question: str):

        if not self.pdf_loaded:
            return "The book file is missing. Please upload it first.", 0.0

        start = time.time()

        # Step 1 — retrieve
        docs = self.db.similarity_search(student_question, k=5)

        # Step 2 — safety filter
        safe_docs = [d for d in docs if responseCheck.is_safe_text(d.page_content)]
        if not safe_docs:
            msg = "That part of the story isn't for our age group 😊"
            self._log("unsafe", "", student_question, 0.0, start)
            return msg, 0.0

        # Step 3 — grounding
        best_passage, support_score = responseCheck.find_best_supported_passage(
            student_question, safe_docs
        )

        if best_passage is None:
            msg = (
                "I'm not sure from this part of the book 🤔\n"
                "Try asking about things shown in this passage!"
            )
            self._log("no_evidence", "", student_question, support_score, start)
            return msg, support_score

        # Step 4 — LLM answer
        prompt = self.PROMPT.format(
            passage=best_passage,
            question=student_question
        )

        try:
            reply = self.llm.invoke(prompt).content
        except Exception:
            reply = "I'm having trouble thinking right now — let's try again! 😊"

        # Step 5 — safety check
        if not responseCheck.is_output_safe(reply):
            reply = "Let's switch to something better for our age group 📚✨"

        self._log("success", best_passage, student_question, support_score, start)
        return reply, support_score

    # -----------------------------------------------------------
    def speak(self, text: str):
        try:
            return TextToSpeech.text_to_speech(text)
        except Exception:
            return None


# ===================================================================
# 📘 STREAMLIT UI WRAPPER (CALLED BY app.py)
# ===================================================================

def ask_the_book_tab(client):
    """
    Streamlit wrapper for ReadingTutor.
    This is what app.py imports and calls.
    """

    st.subheader("📖 Ask The Book — AI Reading Tutor")

    # root project directory
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Available books
    book_options = {
        "The Lost Symbol": "the_lost_symbol.pdf",
        "Halo - The Fall Of Reach": "Halo - The Fall Of Reach.pdf",
    }

    selected_book = st.selectbox("Choose a book:", list(book_options.keys()))

    # Tutor key per book
    tutor_key = f"tutor_{selected_book}"

    # Load tutor ONCE per book
    if tutor_key not in st.session_state:
        with st.spinner("Loading book…"):
            st.session_state[tutor_key] = ReadingTutor(
                pdf_name=book_options[selected_book],
                root_path=project_root
            )

    tutor = st.session_state[tutor_key]

    if not tutor.pdf_loaded:
        st.error(f"PDF not found: {tutor.pdf_path}")
        return

    # User question box
    user_input = st.text_input("Ask a question about the story:")

    if st.button("Ask"):
        with st.spinner("Thinking…"):
            reply, score = tutor.tutor_turn(user_input)

        st.markdown(f"**Tutor**: {reply}")

        audio = tutor.speak(reply)
        if audio:
            st.audio(audio, format="audio/mp3")
