import json
import streamlit as st

from .api_calls import write_to_google_sheet

def _dump_and_write_to_sheets(data):
    data_str = json.dumps(data)
    write_to_google_sheet(data_str)

def add_title_feedback(feedback):
    """
    Add feedback on Job Title Check to Google Sheets
    """
    data = {
        "original": [st.session_state["user_title"], st.session_state["user_desc"]],
        "revised": st.session_state["llm_outputs"][0],
        "feedback": feedback
    }
    _dump_and_write_to_sheets(data)

def add_jd_template_feedback(feedback):
    """
    Add feedback on JD Template Check to Google Sheets
    """
    data = {
        "original": [st.session_state["user_title"], st.session_state["user_desc"]],
        "revised": [st.session_state["llm_outputs"][1], st.session_state["llm_outputs"][2]],
        "feedback": feedback
    }
    _dump_and_write_to_sheets(data)

def add_skills_feedback(feedback):
    """
    Add feedback on Skills Suggestions to Google Sheets
    """
    data = {
        "original": [st.session_state["user_title"], st.session_state["user_desc"]],
        "revised": [st.session_state["llm_outputs"][3]],
        "feedback": feedback
    }
    _dump_and_write_to_sheets(data)
    
def add_job_design_reco_feedback(feedback):
    """
    Add feedback on Job Design Suggestions to Google Sheets
    """
    data = {
        "original": [st.session_state["user_title"], st.session_state["user_desc"]],
        "revised": [st.session_state["llm_outputs"][4]],
        "feedback": feedback
    }
    _dump_and_write_to_sheets(data)

def add_ai_written_feedback(feedback):
    """
    Add feedback on AI Written JD to Google Sheets
    """
    data = {
        "original": [st.session_state["user_title"], st.session_state["user_desc"]],
        "revised": [st.session_state["llm_outputs"][5]],
        "feedback": feedback
    }
    _dump_and_write_to_sheets(data)