"""
st_generate_feedback.py
"""
import json
import re
import urllib3

import streamlit as st

def generate_view() -> None:
    """
    Create the view for the generate feedback tab
    """
    with st.expander("**(Optional) Import from MCF**"):
        st.session_state['mcf_url'] = st.text_input(label="**Enter a valid MCF URL**")

        if st.button("Import from MCF"):
            st.session_state["title_placeholder"] = None
            st.session_state["desc_placeholder"] = None
            try:
                st.session_state["title_placeholder"], st.session_state["desc_placeholder"] = _get_mcf_job(st.session_state['mcf_url'])
            except (urllib3.exceptions.HTTPError, AttributeError, ValueError):
                st.warning("Error. Please check if you have entered a valid MCF URL", icon="⚠️")

    st.session_state['user_title'] = st.text_input("**Title**", value=st.session_state["title_placeholder"])
    st.session_state['user_desc'] = st.text_area("**Description**", value=st.session_state["desc_placeholder"], height=300)

def _get_mcf_job(mcf_url):
    """
    Pulls job from MCF
    """
    http = urllib3.PoolManager()
    regex_matches = re.search('\\-{1}([a-z0-9]{32})\\?', mcf_url + "?")
    mcf_uuid = regex_matches.group(1)
    resp = http.request('GET',f'https://api.mycareersfuture.gov.sg/v2/jobs/{mcf_uuid}')
    mcf_data = json.loads(resp.data)
    mcf_title = mcf_data['title']
    mcf_desc = mcf_data['description']
    mcf_desc = _clean_html(mcf_desc)
    return [mcf_title, mcf_desc]

def _clean_html(text):
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)

    # Replace HTML escape entities with their characters
    cleantext = cleantext.replace('&amp;', '&')
    cleantext = cleantext.replace('&lt;', '<')
    cleantext = cleantext.replace('&gt;', '>')
    cleantext = cleantext.replace('&quot;', '"')
    cleantext = cleantext.replace('&#39;', "'")

    # Remove full HTTP links
    cleantext = re.sub(r'http\S+', '', cleantext)

    return cleantext
