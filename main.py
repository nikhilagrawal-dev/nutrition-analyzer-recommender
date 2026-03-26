import streamlit as st
from app import run_app

def main():
    st.set_page_config(
        page_title="Nutrition Intelligence System",
        layout="wide",
        page_icon="🥗"
    )

    run_app()

if __name__ == "__main__":
    main()