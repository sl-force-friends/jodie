"""
config.py
"""
import os

import streamlit as st

APP_TITLE = "📝 JODIE"
FULL_APP_TITLE = """
    **<span style='color: #cf008a; font-size: 24px;'>Jo</span>b 
    <span style='color: #cf008a; font-size: 24px;'>D</span>escription 
    <span style='color: #cf008a; font-size: 24px;'>I</span>ntelligent 
    <span style='color: #cf008a; font-size: 24px;'>E</span>nhancer**
    """
# TAB_NAMES = ["1️⃣ **Enter JD**", "2️⃣ **AI Feedback**", "3️⃣ **AI Written JD**"] //tabs removed for better experience

API_KEY = st.secrets["JODIE_API_KEY"]
AZURE_ENDPOINT = st.secrets["JODIE_ENDPOINT"]
API_VERSION = "2024-02-15-preview"

SESSION_STATE_DEFAULT_NONE = ["mcf_url", "title_placeholder", "desc_placeholder", "user_title", "user_desc"]
SESSION_STATE_DEFAULT_FALSE = ["read_terms", "generated_ai_feedback"]

