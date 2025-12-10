import streamlit as st


def footer():
    """Footer component for the app"""
    st.markdown(
        """
        <hr>
        <div style='text-align:center; color:gray; font-size:14px; margin-top:20px;'>
            Built with ❤️ by Luffy Learning • Powered by OpenAI
        </div>
        """,
        unsafe_allow_html=True,
    )

