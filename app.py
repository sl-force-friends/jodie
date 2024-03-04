"""
app.py
"""
# Line 4 to 10 is for hosting on streamlit community cloud
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ModuleNotFoundError:
    pass


import urllib3

import asyncio
import streamlit as st

from utils.api_calls import (
    get_mcf_job,
    async_llm_calls
    )
from utils.st_utils import (
    check_password,
    initialise_session_states,
    read_disclaimer,
    set_app_config,
    set_custom_css
    )
from utils.config import (
    APP_TITLE,
    FULL_APP_TITLE
    )

initialise_session_states()
set_app_config()
set_custom_css()

st.subheader(APP_TITLE)
st.markdown(FULL_APP_TITLE, unsafe_allow_html=True)

if not check_password():
    st.stop()

read_disclaimer()

# Step 1: Enter Job Posting
st.session_state['user_title'] = st.text_input("**Enter Job Title**", 
                                               value=st.session_state["title_placeholder"])

st.session_state['user_desc'] = st.text_area("**Enter Job Description**", 
                                             value=st.session_state["desc_placeholder"], 
                                             height=300)

with st.expander("**📥 Import existing job posting from MCF**"):
    st.session_state['mcf_url'] = st.text_input(label="**Enter a valid MCF URL**")
    if st.button("Import from MCF", type='primary'):
        st.session_state["title_placeholder"] = None
        st.session_state["desc_placeholder"] = None
        try:
            st.session_state["title_placeholder"], st.session_state["desc_placeholder"] = get_mcf_job(st.session_state['mcf_url'])
        except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
            st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")

if (st.session_state['user_title'] is not None) and (st.session_state['user_desc'] is not None):
    generate_feedback = st.button("✨ Generate AI Feedback ✨", use_container_width=True)

# Step 2: Generate Feedback
if generate_feedback:
    ai_feedback = st.container()

    ai_feedback.markdown("""
                         <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px;">
                        <strong>Title Check</strong>
                        </div>""",
                        unsafe_allow_html=True)
    
    