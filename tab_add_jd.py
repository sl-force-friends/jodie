"""
tab_add_jd.py
"""
import json
import re
import urllib3

import streamlit as st

def generate_view() -> None:
    """
    Create the view for the generate feedback tab
    """
    st.session_state['user_title'] = st.text_input("**Enter Job Title**", value=st.session_state["title_placeholder"])
    st.session_state['user_desc'] = st.text_area("**Enter Job Description**", value=st.session_state["desc_placeholder"], height=300)

    with st.expander("**Import Job Posting from MCF**"):
        st.session_state['mcf_url'] = st.text_input(label="**Enter a valid MCF URL**")

        if st.button("Import from MCF", type='primary'):
            st.session_state["title_placeholder"] = None
            st.session_state["desc_placeholder"] = None
            try:
                st.session_state["title_placeholder"], st.session_state["desc_placeholder"] = _get_mcf_job(st.session_state['mcf_url'])
            except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
                st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")
