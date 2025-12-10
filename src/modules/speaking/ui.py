import streamlit as st
from src.modules.speaking.coach import SpeechCoach

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

