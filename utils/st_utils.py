"""
Utils related to streamlit app
"""

import streamlit as st

from utils.config import (
    SESSION_STATE_DEFAULT_NONE,
    SESSION_STATE_DEFAULT_FALSE
    )

def set_app_config() -> None:
    """
    Agg configurations
    """
    st.set_page_config(
        page_title="jodie",
        page_icon="🔎",
        layout="centered",
    )

def set_custom_css() -> None:
    """
    Applies custom CSS
    """
    st.markdown("""
            <style>
            #MainMenu {visibility: hidden}
            #header {visibility: hidden}
            #footer {visibility: hidden}
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 3rem;
                padding-right: 3rem;
                }
                
            .stApp a:first-child {
                display: none;
            }
            .css-15zrgzn {display: none}
            .css-eczf16 {display: none}
            .css-jn99sy {display: none}
            </style>
            """, unsafe_allow_html=True)
    
def initialise_session_states() -> None:
    """
    Initialise session states
    """
    for session_state in SESSION_STATE_DEFAULT_NONE:
        if session_state not in st.session_state:
            st.session_state[session_state] = None
    for session_state in SESSION_STATE_DEFAULT_FALSE:
        if session_state not in st.session_state:
            st.session_state[session_state] = False

def disclaimer():
    st.title("🔎 jodie ")
    st.subheader("**:blue[Jo]b :blue[D]escription :blue[I]ntelligent :blue[E]nhancer**")
    st.info("This application is by powered by a Large Language Model (LLMs) and you can use it to generate job posting suggestions. \n \n Treat this as a helpful AI assistant that can provide initial ideas for you to refine. Never trust the responses at face value. If in doubt, don't use the given response.", icon="👋")
    st.info("Your prompts will not be stored by commercial vendors, but may be logged to improve our services. This tool is only for job descriptions.", icon="🚨")
    st.info("By using this service, you acknowledge you recognise the possibility of AI generating inaccurate responses, and you take full responsibility over how you use the generated output.", icon="🤝")

def last_update():
    st.write("This application is in `alpha-stage` testing (v0.2.0, last updated 16/02/2024).")
