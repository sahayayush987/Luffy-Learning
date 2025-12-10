import os
import time
import json
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
    Loads or reuses a Chroma vectorstore for the given PDF.
    """
    return vectorStore.get_vectorstore(
        pdf_path=pdf_path,
        base_chroma_dir=chroma_path
    )


# ===================================================================
# 📚 READING TUTOR CLASS
# ===================================================================

class ReadingTutor:

    SUMMARY_KEYWORDS = [
        "summary", "summarize", "overall", "main idea",
        "whole book", "entire book", "plot", "story about",
        "explain the book", "what is the book about"
    ]

    PROMPT = """
You are a safe, friendly, knowledgeable reading tutor.

RULES:
1. Answer ONLY using the Passage shown below.
2. If the answer is in the passage → explain simply.
3. If not enough information → say:
   "I'm not sure from this part of the book."
4. If the passage has unsafe content → say:
   "That part of the story isn't for our age group."
5. Always stay positive.

AFTER your answer, ALWAYS add:
• One encouraging phrase 💚
• One helpful hint
• One follow-up question

---------------------

📘 Passage:
{passage}

❓ Student Question:
{question}

Now answer following ALL rules.
"""

    # ---------------------------------------------------------------
    def __init__(self, pdf_name: str, root_path: str):

        self.client = get_openai_client()
        self.llm = get_llm()
        self.embeddings = get_embeddings()

        self._setup_db()

        # PDF path
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

    # ---------------------------------------------------------------
    def _setup_db(self):
        """Creates SQLite logging table if missing."""
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

    # ---------------------------------------------------------------
    def _log(self, event, passage, question, score, start_time):
        latency = time.time() - start_time
        self.cursor.execute(
            "INSERT INTO logs VALUES (?,?,?,?,?,?)",
            (time.time(), event, passage, question, score, latency),
        )
        self.conn.commit()

    # ---------------------------------------------------------------
    def _is_summary_request(self, question: str) -> bool:
        q = question.lower()
        return any(k in q for k in self.SUMMARY_KEYWORDS)

    # ---------------------------------------------------------------
    def summarize_whole_book(self):
        """
        Fast full-book summary using top embeddings instead of all pages.
        Executes in under ~15 seconds instead of minutes.
        """
        start = time.time()

        # 1️⃣ Get a manageable number of chunks (top 100 most "central")
        try:
            data = self.db.get()
            all_docs = data["documents"]
        except:
            return "I couldn't process the book. Please re-upload it."

        if not all_docs:
            return "I couldn't read the book yet — please re-upload it."

        # Reduce from thousands → 100 chunks max
        max_chunks = 100
        if len(all_docs) > max_chunks:
            all_docs = all_docs[:max_chunks]

        # 2️⃣ Combine text safely (truncate super-long ones)
        cleaned_chunks = []
        for doc in all_docs:
            cleaned_chunks.append(doc[:800])  # limit per chunk

        combined_text = "\n\n".join(cleaned_chunks)

        # 3️⃣ Single-pass summarization (FAST)
        prompt = f"""
        Summarize this book into a clear, child-friendly 8–12 sentence overview.
        Focus on the main plot, key events, motivations, and themes.
        Do NOT add anything not shown in the text.

        TEXT:
        {combined_text}
        """

        try:
            final_summary = self.llm.invoke(prompt).content
        except:
            final_summary = "I'm having trouble summarizing right now — let's try again! 😊"

        # Safety check
        if not responseCheck.is_output_safe(final_summary):
            final_summary = "That summary isn't suitable for our age group 🌱"

        self._log("full_summary", "", "FULL BOOK SUMMARY REQUEST", 1.0, start)
        return final_summary


    # ---------------------------------------------------------------
    def tutor_turn(self, student_question: str):
        if not self.pdf_loaded:
            return "The book file is missing. Please upload it first.", 0.0

        start = time.time()

        # ============================================================
        # SPECIAL MODE — FULL BOOK SUMMARY
        # ============================================================
        if self._is_summary_request(student_question):
            return self.summarize_whole_book(), 1.0

        # ============================================================
        # NORMAL Q&A MODE
        # ============================================================

        # Step 1: Retrieve passages
        raw_docs = self.db.similarity_search(student_question, k=20)
        if not raw_docs:
            msg = "I couldn't find anything about that part of the story 😊"
            self._log("no_docs", "", student_question, 0.0, start)
            return msg, 0.0

        # Step 2: Safety filter
        safe_docs = [d for d in raw_docs if responseCheck.is_safe_text(d.page_content)]
        if not safe_docs:
            msg = "That part of the story isn't for our age group 😊"
            self._log("unsafe", "", student_question, 0.0, start)
            return msg, 0.0

        # Step 3: Re-ranking
        ranking_prompt = """
        Rank each passage for relevance to the user’s question.
        Respond ONLY with a JSON array of floats (0–1.0).

        Question:
        {q}

        Passages:
        {p}
        """

        passages_string = "\n\n".join(
            [f"--- Passage {i} ---\n{d.page_content}" for i, d in enumerate(safe_docs)]
        )

        try:
            scores = json.loads(
                self.llm.invoke(
                    ranking_prompt.format(q=student_question, p=passages_string)
                ).content
            )
        except:
            scores = [1.0] * len(safe_docs)

        scored = list(zip(safe_docs, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        # Step 4: Top 3 context
        top_docs = [doc.page_content for doc, _ in scored[:3]]
        support_score = sum([s for _, s in scored[:3]]) / 3

        if not top_docs:
            msg = "I'm not sure from this part of the book 🤔"
            self._log("no_evidence", "", student_question, support_score, start)
            return msg, support_score

        merged = "\n\n---\n\n".join(top_docs)

        # Step 5: Template answer
        prompt = self.PROMPT.format(passage=merged, question=student_question)

        try:
            reply = self.llm.invoke(prompt).content
        except:
            reply = "I'm having trouble thinking right now — let's try again! 😊"

        if not responseCheck.is_output_safe(reply):
            reply = "Let's switch to something better for our age group 📚✨"

        self._log("success", merged, student_question, support_score, start)
        return reply, support_score

    # ---------------------------------------------------------------
    def speak(self, text: str):
        try:
            return TextToSpeech.text_to_speech(text)
        except:
            return None


# ===================================================================
# 📘 STREAMLIT UI WRAPPER
# ===================================================================

def ask_the_book_tab(client):

    st.subheader("📖 Ask The Book — AI Reading Tutor")

    project_root = os.path.dirname(os.path.abspath(__file__))

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
