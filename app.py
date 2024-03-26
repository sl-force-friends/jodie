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
    async_api_calls
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
    read_disclaimer
    )
from utils.ui import (
    render_app_title,
    render_custom_css,
    render_subheader_jodie_checks,
    render_subheader_jodie_writes,
    set_app_config
)

initialise_session_states()
set_app_config()
render_custom_css()

render_app_title()

if not check_password():
    st.stop()

read_disclaimer()

# Step 1: Enter JD
st.session_state['user_title'] = st.text_input("**Job Title**",
                                               value=st.session_state["title_placeholder"])

st.session_state['user_desc'] = st.text_area("**Job Description**", 
                                             value=st.session_state["desc_placeholder"],
                                             height=300)

col1, _ , col2 = st.columns([0.9,0.1,2.4])

# Step 1.1: Import from MCF
with col1.popover("Import from MCF"):
    st.session_state['mcf_url'] = st.text_input(label="Enter a valid MCF URL")
    if st.button("Import", type='primary', use_container_width=True):
        st.session_state["title_placeholder"] = None
        st.session_state["desc_placeholder"] = None
        try:
            st.session_state["title_placeholder"], st.session_state["desc_placeholder"], st.session_state["ssoc"] = get_mcf_job(st.session_state['mcf_url'])
            st.rerun()
        except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
            st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")

# Step 1.2: Generate Button
btn_generate_feedback = col2.button("**✨ Ask JODIE ✨**", use_container_width=True)

# Step 2: Generate Feedback
if (btn_generate_feedback) or (st.session_state["llm_outputs"] is not None):
    if (st.session_state['user_title'] is None) or (st.session_state["user_title"] == "") or (st.session_state['user_desc'] is None) or (st.session_state['user_desc'] == ""):
        st.warning("Please enter a valid Job Title and Description", icon="⚠️")
        st.stop()

    # Render subtitle
    render_subheader_jodie_checks()

    # Section A: JODIE CHECKS 
    # Define the Expanders
    expander_job_title_clarity = st.status("**Is my job title clear?**", expanded=False)
    expander_job_desc_content = st.status("**Is there sufficient info in my JD?**", expanded=False)
    expander_skills = st.status("**What additional skills should I emphasize?**", expanded=False)
    expander_job_design_suggestion = st.status("**How can I re-design my job?**", expanded=True)

    # Section B: JODIE WRITES
    render_subheader_jodie_writes()
    expander_ai_written_job_desc = st.status("**AI-Written JD**", expanded=True)


    # Generate Feedback
    if st.session_state["llm_outputs"] is None:
        # Loading messages
        box_job_title_clarity = expander_job_title_clarity.info("_Analysing_ ...", icon="⏳")
        box_job_desc_content_present = expander_job_desc_content.info("_Analysing_ ...", icon="⏳")
        box_job_desc_content_afi = expander_job_desc_content.empty()
        box_skills = expander_skills.info("_Analysing_ ...", icon="⏳")
        box_job_design_suggestions = expander_job_design_suggestion.info("_Analysing_ ...", icon="⏳")
        box_ai_written_job_desc = expander_ai_written_job_desc.info("_Re-writing JD_ ...", icon="⏳")

        asyncio.run(async_api_calls(box_job_title_clarity,
                                    box_job_desc_content_present,
                                    box_job_desc_content_afi,
                                    box_skills,
                                    box_job_design_suggestions,
                                    box_ai_written_job_desc,
                                    expander_job_title_clarity,
                                    expander_job_desc_content,
                                    expander_skills,
                                    expander_job_design_suggestion,
                                    expander_ai_written_job_desc,
                                    st.session_state['user_title'],
                                    st.session_state['user_desc'],
                                    st.session_state["ssoc"]))

        st.toast("JODIE is done - remember to rate the advice!", icon="🎉")
        
    else: # Display content if already generated
        with expander_job_title_clarity as expander_job_title_clarity:
            text_job_title_clarity = st.session_state["llm_outputs"][0]
            if text_job_title_clarity == "This is a clear job title.":
                st.success(f"✅ {text_job_title_clarity}")
            else:
                st.warning(f"⚠️ {text_job_title_clarity}")
            expander_job_title_clarity.update(expanded=True)
        with expander_job_desc_content as expander_job_desc_content:
            text_job_desc_content_present = st.session_state["llm_outputs"][1][0]
            text_job_desc_content_afi = st.session_state["llm_outputs"][1][1]
            st.success(f"✅ {text_job_desc_content_present}")
            if text_job_desc_content_afi != "":
                st.warning(text_job_desc_content_afi)
            expander_job_desc_content.update(expanded=True)
        with expander_skills as expander_skills:
            st.info(st.session_state["llm_outputs"][2])
            expander_skills.update(expanded=True)
        with expander_job_design_suggestion as expander_job_design_suggestion:
            st.info(st.session_state["llm_outputs"][3])
            expander_job_design_suggestion.update(expanded=True)
        with expander_ai_written_job_desc as expander_ai_written_job_desc:
            st.info(st.session_state["llm_outputs"][4])
            expander_ai_written_job_desc.update(expanded=True)

    # Display feedback buttons
    with expander_job_title_clarity:
        with st.popover("Give Feedback"):
            st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
            title_yes, title_no, _ = st.columns([1, 1, 3])
            title_yes.button("👍", key="feedback_title_yes", on_click=add_title_feedback, args=[1])
            title_no.button("👎", key="feedback_title_no", on_click=add_title_feedback, args=[0])
            st.text_area("Any comments 1?")

    with expander_job_desc_content:
        with st.popover("Give Feedback"):
            st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
            jd_template_yes, jd_template_no, _ = st.columns([1, 1, 3])
            jd_template_yes.button("👍", key="feedback_jd_template_yes", on_click=add_jd_template_feedback, args=[1])
            jd_template_no.button("👎", key="feedback_jd_template_no", on_click=add_jd_template_feedback, args=[0])
            st.text_area("Any comments 2?")

    with expander_skills:
        with st.popover("Give Feedback"):
            st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
            skills_yes, skills_no, _ = st.columns([1, 1, 3])
            skills_yes.button("👍", key="feedback_skills_yes", on_click=add_skills_feedback, args=[1])
            skills_no.button("👎", key="feedback_skills_no", on_click=add_skills_feedback, args=[0])
            st.text_area("Any comments 3?")

    with expander_job_design_suggestion:
        with st.popover("Give Feedback"):
            st.markdown("<span style='font-size:14px'><i><b>Do you agree with this recommendation?</i></b></span>", unsafe_allow_html=True)
            design_yes, design_no, _ = st.columns([1, 1, 3])
            design_yes.button("👍", key="feedback_design_yes", on_click=add_job_design_reco_feedback, args=[1])
            design_no.button("👎", key="feedback_design_no", on_click=add_job_design_reco_feedback, args=[0])
            st.text_area("Any comments 4?")

    with expander_ai_written_job_desc:
        col1_ai_written_job_desc, _ , col2_ai_written_job_desc = st.columns([1, 1, 1])

        with col1_ai_written_job_desc.popover("Give Feedback"):
            st.markdown("<span style='font-size:14px'><i><b>Do you agree with this re-write?</i></b></span>", unsafe_allow_html=True)
            ai_written_yes, ai_written_no, _ = st.columns([1, 1, 3])
            ai_written_yes.button("👍", key="feedback_ai_written_yes", on_click=add_ai_written_feedback, args=[1])
            ai_written_no.button("👎", key="feedback_ai_written_no", on_click=add_ai_written_feedback, args=[0])
            st.text_area("Any comments 5?")
    
        with col2_ai_written_job_desc.popover("Copy to Clipboard"):
            text_ai_written_job_desc_with_line_breaks = add_line_breaks(st.session_state['llm_outputs'][4])
            st.markdown(f" ``` {text_ai_written_job_desc_with_line_breaks}")

