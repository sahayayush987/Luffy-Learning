"""
Main entry point for Luffy Learning AI Education Coach

This file imports and runs the main app.
Run with: streamlit run app.py
"""

import src.ui.main_app as main_app

if __name__ == "__main__":
    main_app.main()
    main_app.footer()
