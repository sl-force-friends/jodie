"""
Utils related to streamlit app
"""
import hmac
import streamlit as st

from utils.config import (
    SESSION_STATE_DEFAULT_FALSE,
    SESSION_STATE_DEFAULT_NONE
    )

from utils.config import (
    APP_TITLE,
    FULL_APP_TITLE,
    LAST_UPDATE_DATE
    )

def set_app_config() -> None:
    """
    Agg configurations
    """
    st.set_page_config(
        page_title="JODIE",
        page_icon="🔎",
        layout="centered"
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

def read_disclaimer():
    """
    Disclaimer UI
    """
    if not st.session_state["read_terms"]:
        st.write(f"JODIE is still in `alpha-stage` testing (v0.3.0, last updated {LAST_UPDATE_DATE}).")
        st.info("This tool uses Large Language Model (LLMs) to generate suggestions for your job description.", icon="👋")
        st.info("Your prompts are not be stored by commercial vendors, but may be logged to improve our services. ", icon="🚨")
        st.info("By using this service, you acknowledge you recognise the possibility of AI generating inaccurate responses, and you take full responsibility over how you use the generated output.", icon="🤝")
        if st.button("Accept ✅", use_container_width=True):
            st.session_state["read_terms"] = True
            st.rerun()
        else:
            st.stop()

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True
    # Show input for password.
    st.text_input(
        "Password 🔒", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False
