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
        page_title="JoDIE",
        page_icon="🔎",
        layout="wide",
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
