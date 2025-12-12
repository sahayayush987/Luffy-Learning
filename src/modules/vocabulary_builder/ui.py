import streamlit as st
from openai import OpenAI
from src.modules.vocabulary_builder.vocabulary_builder import generate_vocabulary


def vocabulary_builder_tab(client: OpenAI):
    """
    Streamlit UI for Vocabulary Builder tab.
    """
    
    st.header("💡 Vocabulary Builder")
    st.markdown("Generate vocabulary words with explanations based on your grade level and selected difficulty.")
    
    # Input controls
    col1, col2 = st.columns(2)
    
    with col1:
        grade = st.selectbox(
            "Grade Level",
            ["1-3", "4-6", "7-9", "10-12"],
            index=1,  # Default to 4-6
            help="Select the grade level for vocabulary words"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["easy", "medium", "hard"],
            index=1,  # Default to medium
            help="Select the difficulty level for vocabulary words"
        )
    
    # Generate button
    if st.button("Generate 10 New Words", type="primary"):
        with st.spinner("Generating vocabulary words..."):
            vocab_words = generate_vocabulary(
                client=client,
                grade=grade,
                difficulty=difficulty,
                num_words=10,
            )
        
        if not vocab_words:
            st.error("Could not generate vocabulary words. Please try again.")
            return
        
        # Store in session state
        st.session_state.vocab_words = vocab_words
        st.session_state.vocab_grade = grade
        st.session_state.vocab_difficulty = difficulty
        st.success(f"Generated {len(vocab_words)} vocabulary words!")
    
    # Display vocabulary words (from session state)
    if "vocab_words" in st.session_state and st.session_state.vocab_words:
        st.markdown("---")
        st.subheader(f"📚 Vocabulary Words ({st.session_state.vocab_grade} Grade, {st.session_state.vocab_difficulty.capitalize()} Difficulty)")
        
        for i, word_data in enumerate(st.session_state.vocab_words, start=1):
            with st.expander(f"**{i}. {word_data['word'].upper()}** ({word_data['part_of_speech']})", expanded=False):
                st.markdown(f"**Definition:** {word_data['definition']}")
                st.markdown(f"**Example Sentence:** *{word_data['example_sentence']}*")
                
                if word_data.get('synonyms') and len(word_data['synonyms']) > 0:
                    synonyms_text = ", ".join(word_data['synonyms'])
                    st.markdown(f"**Synonyms:** {synonyms_text}")
        
        st.markdown("---")
        
        # Option to generate new words
        if st.button("Generate New Set of Words", type="secondary"):
            with st.spinner("Generating new vocabulary words..."):
                vocab_words = generate_vocabulary(
                    client=client,
                    grade=st.session_state.vocab_grade,
                    difficulty=st.session_state.vocab_difficulty,
                    num_words=10,
                )
            
            if vocab_words:
                st.session_state.vocab_words = vocab_words
                st.success(f"Generated {len(vocab_words)} new vocabulary words!")
                st.rerun()

