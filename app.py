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

import asyncio

import urllib3
import streamlit as st

from utils.api_calls import (
    get_mcf_job,
    async_llm_calls
    )
from utils.feedback import (
    add_title_feedback,
    add_jd_template_feedback,
    add_skills_feedback,
    add_job_design_reco_feedback,
    add_ai_written_feedback
    )
from utils.st_utils import (
    add_line_breaks,
    check_password,
    initialise_session_states,
    read_disclaimer,
    set_app_config,
    set_custom_css
    )
from utils.config import APP_TITLE

initialise_session_states()
set_app_config()
set_custom_css()

# st.subheader(APP_TITLE)
st.markdown(APP_TITLE, unsafe_allow_html=True)

if not check_password():
    st.stop()

read_disclaimer()

# Step 1: Enter Job Posting
st.session_state['user_title'] = st.text_input("**Job Title**", 
                                            value=st.session_state["title_placeholder"])

st.session_state['user_desc'] = st.text_area("**Job Description**", 
                                            value=st.session_state["desc_placeholder"], 
                                            height=300)

generated_feedback_button = st.empty()

with st.expander("**(Optional) Import from MCF**", expanded=False):

    st.session_state['mcf_url'] = st.text_input(label="**Import from MCF:** Enter a valid MCF URL")

    if st.button("Import from MCF", type='primary', use_container_width=True):
        st.session_state["title_placeholder"] = None
        st.session_state["desc_placeholder"] = None
        try:
            st.session_state["title_placeholder"], st.session_state["desc_placeholder"], st.session_state["ssoc"] = get_mcf_job(st.session_state['mcf_url'])
            st.rerun()
        except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
            st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")

if (st.session_state['user_title'] is not None) and (st.session_state['user_desc'] is not None):
    st.session_state["btn_generate_feedback_pressed"] = generated_feedback_button.button("✨ Ask JODIE ✨", 
                                                                                         use_container_width=True)

# Step 2: Generate Feedback
if st.session_state["btn_generate_feedback_pressed"]:
    if (st.session_state['user_title'] is None) or (st.session_state["user_title"] == "") or (st.session_state['user_desc'] is None) or (st.session_state['user_desc'] == ""):
        st.warning("Please enter a valid Job Title and Description", icon="⚠️")
        st.stop()
    st.divider()
    st.markdown("""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px; text-align: center;">
                    <strong>JODIE Checks 🔎</strong>
                </div>
                <br>""", unsafe_allow_html=True)
    
    job_title_check_expander = st.expander("**Is my job title clear?**", expanded=True)
    jd_template_check_expander = st.expander("**Is there sufficient info in my JD?**", expanded=True)
    skills_check_expander = st.expander("**What are additional skills should I emphasize?**", expanded=True)
    job_design_suggestion_expander = st.expander("**How can I re-design my job?**", expanded=True)

    with job_title_check_expander:
        title_box = st.empty()
        title_box = st.info("_Analysing_ ...", icon="⏳")
        
    with jd_template_check_expander:
        jd_template_box = st.empty()
        jd_template_box = st.info("_Analysing_ ...", icon="⏳")
        to_remove_content_box = st.empty()

    with skills_check_expander:
        skills_box = st.empty()
        skills_box = st.info("_Analysing_ ...", icon="⏳")

    with job_design_suggestion_expander:
        suggestions_box = st.empty()
        suggestions_box = st.info("_Analysing_ ...", icon="⏳")

    st.divider()
    st.markdown("""
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px; text-align: center;">
                    <strong>JODIE Writes ✏️</strong>
                </div>
                <br>""", unsafe_allow_html=True)

    ai_written_jd_expander = st.expander("**AI-Written JD**", expanded=True)

    with ai_written_jd_expander:
        ai_version_box = st.empty()
        ai_version_box = st.info("_Re-writing the JD with AI_ ...", icon="⏳")


    asyncio.run(async_llm_calls(title_box,
                                jd_template_box,
                                to_remove_content_box,
                                skills_box,
                                suggestions_box,
                                ai_version_box,
                                st.session_state['user_title'],
                                st.session_state['user_desc'],
                                st.session_state["ssoc"]))

    st.toast("Feedback generated - remember to rate it!",
             icon="🎉")

    with st.expander("Copy to Clipboard"):
        st.markdown(f" ``` {add_line_breaks(st.session_state['llm_outputs'][-1])}")

    with job_title_check_expander:
        st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
        title_yes, title_no, _ = st.columns([1, 1, 10])
        title_yes.button("👍", key="feedback_title_yes", on_click=add_title_feedback, args=(1, None))
        title_no.button("👎", key="feedback_title_no", on_click=add_title_feedback, args=(0, None))

    with jd_template_check_expander:
        st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
        jd_template_yes, jd_template_no, _ = st.columns([1, 1, 10])
        jd_template_yes.button("👍", key="feedback_jd_template_yes", on_click=add_jd_template_feedback, args=(1, None))
        jd_template_no.button("👎", key="feedback_jd_template_no", on_click=add_jd_template_feedback, args=(0, None))
    
    with skills_check_expander:
        st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
        skills_yes, skills_no, _ = st.columns([1, 1, 10])
        skills_yes.button("👍", key="feedback_skills_yes", on_click=add_skills_feedback, args=(1, None))
        skills_no.button("👎", key="feedback_skills_no", on_click=add_skills_feedback, args=(0, None))
    
    with job_design_suggestion_expander:
        st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
        design_yes, design_no, _ = st.columns([1, 1, 10])
        design_yes.button("👍", key="feedback_design_yes", on_click=add_job_design_reco_feedback, args=(1, None))
        design_no.button("👎", key="feedback_design_no", on_click=add_job_design_reco_feedback, args=(0, None))
    
    with ai_written_jd_expander:
        st.markdown("<span style='font-size:14px'><i><b>Do you agree with this re-write?</i></b></span>", unsafe_allow_html=True)
        ai_written_yes, ai_written_no, _ = st.columns([1, 1, 10])
        ai_written_yes.button("👍", key="feedback_ai_written_yes", on_click=add_ai_written_feedback, args=(1, None))
        ai_written_no.button("👎", key="feedback_ai_written_no", on_click=add_ai_written_feedback, args=(0, None))
