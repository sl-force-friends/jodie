import json
import re
import urllib3

import asyncio
import streamlit as st

JODIE_API_KEY = st.secrets["JODIE_BACKEND_API_KEY"]

def get_mcf_job(mcf_url: str) -> list[str]:
    """
    Pulls job from MCF
    """
    http = urllib3.PoolManager()
    regex_matches = re.search('([a-f0-9]{32})', mcf_url)
    if not regex_matches:
        raise ValueError("Invalid MCF URL")
    mcf_uuid = regex_matches.group(1)
    try:
        resp = http.request('GET',f'https://api.mycareersfuture.gov.sg/v2/jobs/{mcf_uuid}')
    except urllib3.exceptions.HTTPError as e:
        raise urllib3.exceptions.HTTPError("Cannot query MCF or invalid MCF URL. Please try again.") from e
    mcf_data = json.loads(resp.data)
    try:
        mcf_title = mcf_data['title']
        mcf_desc = mcf_data['description']
    except AttributeError as e:
        raise AttributeError("Cannot find job title or description from MCF. Please try again.") from e
    mcf_desc = _clean_html(mcf_desc)
    return [mcf_title, mcf_desc]

def _clean_html(text: str) -> str:
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

async def async_llm_calls(title_box,
                          present_content_box,
                          missing_content_box,
                          to_remove_content_box,
                          suggestions_box,
                          ai_version_box,
                          title,
                          description):
    """
    Asynchronous function to run the main logic
    """
    results = await asyncio.gather(
        check_job_title(title_box, title, description),
        check_positive_content(present_content_box, missing_content_box, title, description),
        check_negative_content(to_remove_content_box, title, description),
        generate_recommendations(suggestions_box, title, description),
        generate_ai_version(ai_version_box, title, description)
    )
    st.session_state["ai_feedback"] = results

async def check_job_title(title_box, title, description):
    """
    Check if job title is present
    """
    if not title:
        title_box.warning("Please enter a job title", icon="⚠️")
        return None
    return title

async def check_positive_content(present_content_box, missing_content_box, title, description):
    """
    Check if job description is present
    """
    if not description:
        missing_content_box.warning("Please enter a job description", icon="⚠️")
        return None
    return description

async def check_negative_content(to_remove_content_box, title, description):
    """
    Check if job description is present
    """
    if not description:
        to_remove_content_box.warning("Please enter a job description", icon="⚠️")
        return None
    return description

async def generate_recommendations(suggestions_box, title, description):
    """
    Generate recommendations
    """
    suggestions_box.info("Generating recommendations...")
    return None

async def generate_ai_version(ai_version_box, title, description):
    """
    Generate AI version
    """
    ai_version_box.info("Generating AI version...")
    return None
