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
import time
import asyncio
import streamlit as st

from utils.api_calls import (
    get_mcf_job,
    async_llm_calls
    )
from utils.st_utils import (
    add_line_breaks,
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
with st.expander("**Step 1: Enter your JD**", expanded=True):
    st.session_state['user_title'] = st.text_input("**Enter Job Title**", 
                                                value=st.session_state["title_placeholder"])

    st.session_state['user_desc'] = st.text_area("**Enter Job Description**", 
                                                value=st.session_state["desc_placeholder"], 
                                                height=300)

    st.session_state['mcf_url'] = st.text_input(label="**(Optional) Import from MCF:** Enter a valid MCF URL")
    if st.button("Import from MCF", type='primary', use_container_width=True):
        st.session_state["title_placeholder"] = None
        st.session_state["desc_placeholder"] = None
        try:
            st.session_state["title_placeholder"], st.session_state["desc_placeholder"] = get_mcf_job(st.session_state['mcf_url'])
            st.rerun()
        except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
            st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")

if (st.session_state['user_title'] is not None) and (st.session_state['user_desc'] is not None):
    st.session_state["btn_generate_feedback_pressed"] = st.button("✨ Step 2: Generate AI Feedback ✨", use_container_width=True)

# Step 2: Generate Feedback
if st.session_state["btn_generate_feedback_pressed"]:
    st.divider()
    st.subheader("AI Feedback")
    with st.expander("**Is my job title clear?**", expanded=True):
        title_box = st.empty()
        title_box = st.info("Analysing ...", icon="⏳")
    with st.expander("**Is there sufficient info in my JD?**", expanded=True):
        jd_template_box = st.empty()
        jd_template_box = st.info("Analysing ...", icon="⏳")
        to_remove_content_box = st.empty()
    with st.expander("**How can I re-design my job?**", expanded=True):
        suggestions_box = st.empty()
        suggestions_box = st.info("Analysing ...", icon="⏳")
    
    st.divider()
    with st.expander("**AI-Written JD**", expanded=True):
        ai_version_box = st.empty()
        ai_version_box = st.info("**Re-writing the JD with AI** ...", icon="⏳")

    asyncio.run(async_llm_calls(title_box,
                                jd_template_box,
                                to_remove_content_box,
                                suggestions_box,
                                ai_version_box,
                                st.session_state['user_title'],
                                st.session_state['user_desc']))
    
    with st.expander("Copy to Clipboard"):
        st.markdown(f" ``` {add_line_breaks(st.session_state['llm_outputs'][-1])}")
