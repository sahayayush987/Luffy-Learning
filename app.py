"""
Main entry point for Luffy Learning AI Education Coach

This file imports and runs the main app.
Run with: streamlit run app.py
"""

import streamlit as st
import src.ui.main_app as main_app

st.set_page_config(
    page_title="AI Education Coach",
    page_icon="🐶",
    initial_sidebar_state="expanded",
    layout="wide"
)


if __name__ == "__main__":
    main_app.main()
    main_app.footer()
