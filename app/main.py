import streamlit as st
import sys
import os

# ── main.py ──────────────────────────────────────────────────────────────────

# Ensure the root directory is in sys.path to find modules
sys.path.append(os.getcwd())

from app import app

def main():
    """
    Entry point for the Nutrition Intelligence System.
    Sets the page configuration and runs the app router.
    """
    st.set_page_config(
        page_title="Nutrition Intelligence System",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    app.run()

if __name__ == "__main__":
    main()
