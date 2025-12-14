import streamlit as st
import os


def render_sidebar():
    """
    Renders the sidebar with navigation, settings, and app information
    """
    with st.sidebar:

        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        logo_path = os.path.join(project_root, "logo.png")
        
        if os.path.exists(logo_path):
            st.image(logo_path, width='content')
        else:
            # Fallback if logo not found
            st.title("🐶 Luffy Learning")
        st.markdown("---")
        
        # Navigation Section
        st.header("📚 Navigation")
        
        # Quick links to tabs
        st.markdown("""
        - 🗣️ **Speaking Practice** - Improve pronunciation
        - 📖 **Ask The Book** - AI reading tutor
        - 📚 **Curriculum** - Analyze curriculum
        - 🎓 **MCQ Generator** - Generate practice questions
        - 💡 **Vocabulary Builder** - Build vocabulary skills
        - 📚 **Luffy Book Recommendations** - Get personalized book recommendations
        """)
        
        st.markdown("---")
        
        # Settings Section
        st.header("⚙️ Settings")
        
        # Theme selector (if needed)
        # st.selectbox("Theme", ["Light", "Dark", "Auto"])
        
        # Show API status
        api_key_set = bool(os.getenv("OPENAI_API_KEY"))
        if api_key_set:
            st.success("✅ API Key Configured")
        else:
            st.warning("⚠️ API Key Not Set")
            st.info("Add OPENAI_API_KEY to your .env file")
        
        st.markdown("---")
        
        # App Information
        st.header("ℹ️ About")
        st.markdown("""
        **Luffy Learning** is an AI-powered educational platform designed to help students improve their learning experience.
        
        **Features:**
        - 🗣️ Speaking practice with pronunciation analysis
        - 📖 Interactive book tutoring
        - 📚 Curriculum summarization
        - 🎓 MCQ question generation
        - 💡 Vocabulary building with grade-level words
        - 📚 Personalized book recommendations with cover images and buy links
        
        **Powered by:**
        - OpenAI GPT models
        - Streamlit
        - ChromaDB
        """)
        
        st.markdown("---")
        
        # Version/Status
        st.markdown("""
        <div style='text-align:center; color:gray; font-size:12px;'>
            Version 1.0.0<br>
            Built with ❤️
        </div>
        """, unsafe_allow_html=True)
        
        # Help/Support
        st.markdown("---")
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **Common Issues:**
            - PDF not found? Place books in `data/novels/`
            - API errors? Check your `.env` file
            - Slow loading? Vector stores are created on first use
            
            **Documentation:**
            See `README.md` for setup instructions.
            """)

