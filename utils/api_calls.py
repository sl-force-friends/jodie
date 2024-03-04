import json
import re
import time
import urllib3

import aiohttp
import asyncio
import streamlit as st

JODIE_BACKEND_API_KEY = st.secrets["JODIE_BACKEND_API_KEY"]

JODIE_API_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': JODIE_BACKEND_API_KEY
}

BASE_ENDPOINT = "https://jodie-api.fly.dev"


def get_mcf_job(mcf_url: str) -> list[str]:
    """
    Pulls job from MCF
    """
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
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
                          jd_template_box,
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
        check_positive_content(jd_template_box, title, description),
        check_negative_content(to_remove_content_box, title, description),
        generate_recommendations(suggestions_box, title, description),
        generate_ai_version(ai_version_box, title, description)
    )
    st.session_state["llm_outputs"] = results

async def check_job_title(title_box, title, description):
    """
    Check if job title is present
    """
    result = await _async_api_call(BASE_ENDPOINT + "/title_check",
                                  {"job_title": title, "job_description": description})
    if int(result):
        title_box.success("**Title Check:** This is a clear job title.", icon="✅")
    else:
        alternative_titles = await _async_api_call(BASE_ENDPOINT + "/alt_titles",
                                                   {"job_title": title, "job_description": description})
        title_box.warning(f"**Title Check:** You may want to consider these alternative titles: {alternative_titles}", icon="📣")

async def check_positive_content(jd_template_box, title, description):
    """
    Check if job description is present
    """
    result = await _async_api_call(BASE_ENDPOINT + "/positive_content_check",
                                  {"job_title": title, "job_description": description})
    
    result = json.loads(result)

    text = "**Content Check:** \n \n"

    for count, item in enumerate(result.keys()):
        if result[item]:
            item_formatted = item.replace("_", " ").capitalize()
            text += f"\n {count+1}. {item_formatted}: ✅"
        else:
            item_formatted = item.replace("_", " ").capitalize()
            text += f"\n {count+1}. {item_formatted}: ❓"
    
    jd_template_box.info(text, icon="🔎")

async def check_negative_content(to_remove_content_box, title, description):
    """
    Check if job description is present
    """
    result = await _async_api_call(BASE_ENDPOINT + "/negative_content_check",
                                  {"job_title": title, "job_description": description})
    
    result = json.loads(result)

    text = "You may want to consider removing the following: "

    for count, item in enumerate(result.keys()):
        if result[item]:
            item_formatted = item.replace("_", " ").capitalize()
            text += f"\n {count+1}. {item_formatted}"

    to_remove_content_box.warning(text, icon="📣")

async def generate_recommendations(suggestions_box, title, description):
    """
    Generate recommendations
    """
    stream = _async_api_call_streaming(BASE_ENDPOINT + "/job_design_suggestions",
                                  {"job_title": title, "job_description": description})
    
    text = "**Job Design Suggestions:** \n \n"

    async for chunk in stream:
        chunk = chunk.decode('utf-8')
        for char in chunk:
            text += char
            suggestions_box.info(text, icon = "💡")
            time.sleep(0.01)
        
async def generate_ai_version(ai_version_box, title, description):
    """
    Generate AI version
    """
    stream = _async_api_call_streaming(BASE_ENDPOINT + "/rewrite_jd",
                                  {"job_title": title, "job_description": description})
    
    text = ""

    async for chunk in stream:
        chunk = chunk.decode('utf-8')
        for char in chunk:
            text += char
            time.sleep(0.01)
            ai_version_box.info(text)


async def _async_api_call(url, data):
    """
    Asynchronous API call
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session: 
        async with session.post(url, data=json.dumps(data), headers=JODIE_API_HEADERS) as response:  # Makes a POST request
            response_data = await response.text()  
            return response_data

async def _async_api_call_streaming(url, data):
    """
    Asynchronous API call with streaming response.
    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:  # Creates a session
        async with session.post(url, data=json.dumps(data), headers=JODIE_API_HEADERS) as response:
            async for chunk in response.content:
                yield chunk
