import streamlit as st
import numpy as np
from dotenv import load_dotenv
from analyzer import detect_errors
from feedback import safe_child_friendly_feedback
from audio_cleaner import clean_audio

load_dotenv()

# ============================================================
# 🔤 PHONEME TIPS
# ============================================================
PHONEME_TIPS = {
    "th": "Place your tongue gently between your teeth and blow air softly.",
    "r": "Pull your tongue slightly back and avoid touching the roof of your mouth.",
    "l": "Touch the tip of your tongue to the ridge behind your upper teeth.",
    "s": "Keep your tongue low and blow air over the top.",
    "ch": "Start with a 't' sound and quickly push into a 'sh' sound.",
}


# ============================================================
# ⚡ Cosine Similarity (safe)
# ============================================================
def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return 0 if denom == 0 else float(np.dot(a, b) / denom)


# ============================================================
# ⚡ SPEECH COACH (Highly Optimized)
# ============================================================
class SpeechCoach:
    """
    Fast + optimized:
    - Lazy audio imports
    - Batched embeddings
    - Minimal OpenAI calls
    """

    def __init__(self, client):
        self.client = client

    # -------------------------------------------------------
    # 📘 PASSAGE GENERATION (fast)
    # -------------------------------------------------------
    def generate_passage(self, grade, difficulty):
        rules = {
            "Easy": "Use simple words, short sentences, concrete ideas.",
            "Medium": "Use richer vocabulary and descriptive words.",
            "Hard": "Use advanced vocabulary and complex structure.",
            "Give Me God Of War": "Use epic, mythic, dramatic storytelling."
        }

        prompt = f"""
        Create a reading passage for Grade {grade}.
        Length: 1–2 sentences, 30–40 words.
        Tone: cheerful.
        Difficulty: {difficulty}
        Rules: {rules[difficulty]}
        """

        res = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You generate leveled reading passages for students."},
                {"role": "user", "content": prompt}
            ]
        )

        return res.choices[0].message.content.strip()

    # -------------------------------------------------------
    # 🎧 AUDIO ENHANCEMENT (lazy-load heavy libs)
    # -------------------------------------------------------
    def enhance_audio(self, audio_bytes):
        return clean_audio(audio_bytes)

    # -------------------------------------------------------
    # 🔄 TRANSCRIPTION
    # -------------------------------------------------------
    def transcribe_audio(self, enhanced_bytes):
        return self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=("enhanced.wav", enhanced_bytes, "audio/wav")
        ).text

    # -------------------------------------------------------
    # 🧠 ERRORS + FEEDBACK
    # -------------------------------------------------------
    def evaluate_transcript(self, expected_text, transcript):
        errors = detect_errors(expected_text, transcript)
        feedback = safe_child_friendly_feedback(errors)
        return errors, feedback

    # -------------------------------------------------------
    # 🧠 BATCH EMBEDDING PRONUNCIATION SCORING (super fast)
    # -------------------------------------------------------
    def phoneme_score(self, expected_text, transcript):
        exp_words = expected_text.lower().split()
        spk_words = transcript.lower().split()
    
        # Limit to word pairs that exist
        words_to_compare = []
        for i in range(len(exp_words)):
            if i < len(spk_words):
                words_to_compare.append((exp_words[i], spk_words[i]))
            else:
                words_to_compare.append((exp_words[i], None))
    
        # ------------------------------------------
        # 1️⃣ Batch embed all words in ONE call
        # ------------------------------------------
        batch_inputs = []
        for exp, spk in words_to_compare:
            batch_inputs.append(exp)
            batch_inputs.append(spk if spk else "<missing>")   # IMPORTANT FIX ✔
    
        embeds = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=batch_inputs
        ).data
    
        # Reshape embeddings
        exp_embeds = embeds[0::2]
        spk_embeds = embeds[1::2]
    
        scores = []
        suggestions = []
    
        for (exp, spk), e_emb, s_emb in zip(words_to_compare, exp_embeds, spk_embeds):
    
            if spk is None or spk == "<missing>":
                scores.append((exp, 0.0))
                suggestions.append(f"Try pronouncing **{exp}** clearly.")
                continue
    
            raw = cosine_sim(e_emb.embedding, s_emb.embedding)
            score = (raw + 1) / 2  # normalize to 0–1
    
            scores.append((exp, score))
    
            if score < 0.65:
                for ph, tip in PHONEME_TIPS.items():
                    if ph in exp:
                        suggestions.append(f"For **{exp}**, {tip}")
                        break
                else:
                    suggestions.append(f"Try saying **{exp}** slowly and clearly.")
    
        return scores, suggestions



# ============================================================
# 🎤 STREAMLIT UI (Optimized)
# ============================================================
def evaluate_speaking(client):

    coach = SpeechCoach(client)

    # ----------------------------------
    # 📘 Passage Selection
    # ----------------------------------
    grade = st.selectbox("Select Grade Level:", list(range(1, 13)))
    difficulty = st.selectbox("Difficulty:", ["Easy", "Medium", "Hard", "Give Me God Of War"])

    if "passage" not in st.session_state:
        st.session_state.passage = ""

    if st.button("Generate Passage"):
        st.session_state.passage = coach.generate_passage(grade, difficulty)

    st.subheader("📘 Reading Passage")
    expected_text = st.text_area(
        "Edit or customize:",
        st.session_state.passage,
        height=120,
    )

    # ----------------------------------
    # 🎤 Audio Input
    # ----------------------------------
    audio_file = st.audio_input("🎤 Read it aloud and click Stop")

    # ----------------------------------
    # 🧠 ANALYZE
    # ----------------------------------
    if st.button("Analyze Reading", type="primary"):

        if not audio_file:
            st.warning("⚠️ Please record audio first.")
            st.stop()

        # 1️⃣ Enhance
        with st.spinner("Enhancing audio…"):
            enhanced = coach.enhance_audio(audio_file.getvalue())
        st.audio(enhanced, format="audio/wav")

        # 2️⃣ Transcribe
        with st.spinner("Transcribing…"):
            transcript = coach.transcribe_audio(enhanced)
        st.session_state.transcript = transcript

        # 3️⃣ Errors + Feedback
        errors, feedback = coach.evaluate_transcript(expected_text, transcript)
        st.session_state.errors = errors
        st.session_state.feedback = feedback

        # 4️⃣ Pronunciation Scores
        with st.spinner("Analyzing pronunciation…"):
            scores, tips = coach.phoneme_score(expected_text, transcript)
        st.session_state.phoneme_scores = scores
        st.session_state.phoneme_tips = tips

    # ----------------------------------
    # 📄 OUTPUT
    # ----------------------------------
    if "transcript" in st.session_state:
        st.subheader("🗣️ Transcript")
        st.write(st.session_state.transcript)

    if "errors" in st.session_state:
        st.subheader("🔍 Words to Practice")
        st.write(st.session_state.errors or "None! 🎉")

    if "feedback" in st.session_state:
        st.subheader("💬 Coach Feedback")
        st.write(st.session_state.feedback)

    # ----------------------------------
    # 🎨 Pronunciation Heatmap
    # ----------------------------------
    if "phoneme_scores" in st.session_state:
        st.subheader("🎨 Pronunciation Heatmap")

        heatmap = ""
        for word, score in st.session_state.phoneme_scores:
            color = (
                "#2ecc71" if score > 0.85 else
                "#f1c40f" if score > 0.60 else
                "#e74c3c"
            )
            heatmap += (
                f"<span style='background-color:{color}; padding:4px; "
                f"margin:2px; border-radius:4px;'>{word}</span> "
            )

        st.markdown(heatmap, unsafe_allow_html=True)

    # ----------------------------------
    # 🎯 Articulation Tips
    # ----------------------------------
    if "phoneme_tips" in st.session_state:
        st.subheader("🎯 Articulation Tips")
        for tip in st.session_state.phoneme_tips:
            st.write("• " + tip)
