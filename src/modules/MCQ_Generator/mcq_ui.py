import streamlit as st
from openai import OpenAI
from src.modules.curriculum.helpers import extract_text_from_file
from src.modules.MCQ_Generator.mcq_generator import generate_mcqs


def mcq_generator_tab(client: OpenAI):

    st.header("📝 MCQ Generator")

    uploaded_file = st.file_uploader(
        "Upload curriculum / reading passage (PDF or TXT)",
        type=["pdf", "txt"],
    )

    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of questions", 3, 15, 5)
    with col2:
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)

    if uploaded_file:
        # Initialize session state for MCQs if not exists
        if "mcqs" not in st.session_state:
            st.session_state.mcqs = None
        
        text = extract_text_from_file(uploaded_file)

        if st.button("Generate MCQs", type="primary"):
            with st.spinner("Generating questions..."):
                mcqs = generate_mcqs(
                    client=client,
                    source_text=text,
                    num_questions=num_questions,
                    difficulty=difficulty,
                )

            if not mcqs:
                st.error("Could not generate MCQs. Try another document.")
                st.session_state.mcqs = None
                return

            st.session_state.mcqs = mcqs
            st.success(f"Generated {len(mcqs)} questions!")

        # ---------------------------
        # Display MCQs (from session state)
        # ---------------------------
        if st.session_state.mcqs:
            for i, q in enumerate(st.session_state.mcqs, start=1):

                st.markdown(f"### Q{i}. {q['question']}")

                # Let user choose answer
                user_choice = st.radio(
                    "Select an answer:",
                    q["options"],
                    key=f"mcq_{i}",
                    index=None,
                )

                # Determine correct option
                correct_idx = ord(q["answer"]) - ord("A")
                correct_option = q["options"][correct_idx]

                # Reveal result ONLY after selection
                if user_choice is not None:
                    if user_choice == correct_option:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. Correct answer: **{correct_option}**")

                    st.info(f"**Explanation:** {q['explanation']}")

                st.markdown("---")
