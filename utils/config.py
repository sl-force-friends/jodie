"""
config.py
"""
import os

APP_TITLE = "🔎 JoDIE \n **:blue[Jo]b :blue[D]escription :blue[I]ntelligent :blue[E]nhancer**"
TAB_NAMES = ["1️⃣ **Enter JD**", "2️⃣ **AI-Feedback**", "3️⃣ **Re-Written JD**"]

API_KEY = os.getenv("JODIE_API_KEY")
AZURE_ENDPOINT = os.getenv("JODIE_ENDPOINT", "MISSING")
API_VERSION = "2024-02-15-preview"

SESSION_STATE_DEFAULT_NONE = ["mcf_url", "title_placeholder", "desc_placeholder", "user_title", "user_desc"]
SESSION_STATE_DEFAULT_FALSE = ["generated_ai_feedback"]
