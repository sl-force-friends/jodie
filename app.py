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

def _add_line_breaks(text, length=150):
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        words = line.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) <= length:
                current_line += word + " "
            else:
                new_lines.append(current_line.strip())
                current_line = word + " "
        new_lines.append(current_line.strip())
    return "\n".join(new_lines)

st.subheader(APP_TITLE)
st.markdown(FULL_APP_TITLE, unsafe_allow_html=True)

if not check_password():
    st.stop()

read_disclaimer()


col1, col2 = st.columns(2)

# Step 1: Enter Job Posting
st.session_state['user_title'] = col1.text_input("**Enter Job Title**", 
                                               value=st.session_state["title_placeholder"])

st.session_state['user_desc'] = col1.text_area("**Enter Job Description**", 
                                             value=st.session_state["desc_placeholder"], 
                                             height=300)


with col1.expander("**📥 Import existing job posting from MCF**"):
    st.session_state['mcf_url'] = st.text_input(label="**Enter a valid MCF URL**")
    if st.button("Import from MCF", type='primary'):
        st.session_state["title_placeholder"] = None
        st.session_state["desc_placeholder"] = None
        try:
            st.session_state["title_placeholder"], st.session_state["desc_placeholder"] = get_mcf_job(st.session_state['mcf_url'])
            st.rerun()
        except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
            st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")

if (st.session_state['user_title'] is not None) and (st.session_state['user_desc'] is not None):
    st.session_state["btn_generate_feedback_pressed"] = col1.button("✨ Generate AI Feedback ✨", use_container_width=True)

# Step 2: Generate Feedback
if st.session_state["btn_generate_feedback_pressed"]:
    title_box = col2.empty()
    title_box = col2.info("**Title Check:** Analysing ...", icon="⏳")
    jd_template_box = col2.empty()
    jd_template_box = col2.info("**Content Check:** Analysing ...", icon="⏳")
    to_remove_content_box = col2.empty()
    st.divider()
    col3, col4 = st.columns(2)
    suggestions_box = col3.empty()
    suggestions_box = col3.info("**Job Design Suggestions:** Analysing ...", icon="⏳")
    ai_version_box = col4.empty()
    ai_version_box = col4.info("**Re-writing the JD with AI** ...", icon="⏳")

    asyncio.run(async_llm_calls(title_box,
                                jd_template_box,
                                to_remove_content_box,
                                suggestions_box,
                                ai_version_box,
                                st.session_state['user_title'],
                                st.session_state['user_desc']))
    

    with col4.expander("Copy to Clipboard"):
        st.write(f" ``` {_add_line_breaks(st.session_state['llm_outputs'][-1])}")
