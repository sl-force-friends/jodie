import streamlit as st

from .config import APP_TITLE

def set_app_config() -> None:
    """
    Agg configurations
    """
    st.set_page_config(
        page_title="JODIE",
        page_icon="🔎",
        layout="centered",
    )

def render_custom_css() -> None:
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

def render_app_title() -> None:
    """
    Renders app title
    """
    st.markdown(APP_TITLE, unsafe_allow_html=True)

def render_subheader_jodie_checks() -> None:
    """
    Renders subheader of "JODIE CHECKS"
    """
    st.divider()
    st.markdown("""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px; text-align: center;">
                <strong>JODIE Checks 🔎</strong>
            </div>
            <br>""", unsafe_allow_html=True)

def render_subheader_jodie_writes() -> None:
    """
    Renders subheader of "JODIE WRITES"
    """
    st.divider()
    st.markdown("""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px; text-align: center;">
                    <strong>JODIE Writes ✏️</strong>
                </div>
                <br>""", unsafe_allow_html=True)
