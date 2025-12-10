"""
Main entry point for Luffy Learning AI Education Coach

This file imports and runs the main app from the new structured package.
For development, you can also run: streamlit run src/ui/main_app.py
"""

from src.ui.main_app import main, footer

if __name__ == "__main__":
    main()
    footer()
