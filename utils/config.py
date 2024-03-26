"""
config.py
"""
import streamlit as st

LAST_UPDATE_DATE = "04-03-2024"

APP_TITLE = """
    <div style='text-align: center; padding-bottom: 20px;'>
        <b><span style='color: #cf008a; font-size: 24px;'>✨ JODIE</span> <br>
        <span style='color: #cf008a'>JO</span>b 
        <span style='color: #cf008a'>D</span>escription 
        <span style='color: #cf008a'>I</span>ntelligent 
        <span style='color: #cf008a'>E</span>nhancer</b>
    </div>
    """

API_KEY = st.secrets["JODIE_API_KEY"]
AZURE_ENDPOINT = st.secrets["JODIE_ENDPOINT"]
API_VERSION = "2024-02-15-preview"

SESSION_STATE_DEFAULT_NONE = ["mcf_url", "title_placeholder", "desc_placeholder", "user_title", "user_desc", "llm_outputs"]
SESSION_STATE_DEFAULT_FALSE = ["read_terms", "mcf_expander", "btn_generate_feedback_pressed"]
