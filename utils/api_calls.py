import json
import re
import time
import urllib3
from datetime import datetime
from typing import Any

import aiohttp
import asyncio
import gspread
import streamlit as st
from google.oauth2 import service_account
from streamlit.delta_generator import DeltaGenerator

BASE_ENDPOINT = st.secrets["JODIE_BACKEND_ENDPOINT"]
JODIE_BACKEND_API_KEY = st.secrets["JODIE_BACKEND_API_KEY"]
JODIE_API_HEADERS = {
    'Content-Type': 'application/json',
    'x-api-key': JODIE_BACKEND_API_KEY
}


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
        ssoc = mcf_data['ssocCode']
    except AttributeError as e:
        raise AttributeError("Cannot find job title or description from MCF. Please try again.") from e
    mcf_desc = _clean_html(mcf_desc)
    return [mcf_title, mcf_desc, ssoc]

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

async def async_api_calls(box_job_title_clarity: DeltaGenerator,
                          box_job_desc_content_present: DeltaGenerator,
                          box_job_desc_content_afi: DeltaGenerator,
                          box_skills: DeltaGenerator,
                          box_job_design_suggestions: DeltaGenerator,
                          box_ai_written_job_desc: DeltaGenerator,
                          expander_job_title_clarity: DeltaGenerator,
                          expander_job_desc_content: DeltaGenerator,
                          expander_skills: DeltaGenerator,
                          expander_job_design_suggestion: DeltaGenerator,
                          expander_ai_written_job_desc: DeltaGenerator,
                          job_title: str,
                          job_desc: str, 
                          ssoc: int) -> None:
    """
    Asynchronous function to run the main logic
    """
    results = await asyncio.gather(
        check_job_title(box_job_title_clarity,
                        expander_job_title_clarity,
                        job_title,
                        job_desc),
        check_content(box_job_desc_content_present,
                      box_job_desc_content_afi,
                      expander_job_desc_content,
                      job_title,
                      job_desc),
        get_skills(box_skills,
                   expander_skills,
                   ssoc),
        generate_recommendations(box_job_design_suggestions,
                                 expander_job_design_suggestion,
                                 job_title,
                                 job_desc),
        generate_ai_version(box_ai_written_job_desc,
                            expander_ai_written_job_desc,
                            job_title,
                            job_desc)
    )
    st.session_state["llm_outputs"] = results

async def check_job_title(box_job_title_clarity: DeltaGenerator,
                          expander_job_title_clarity: DeltaGenerator,
                          job_title: str,
                          job_desc: str) -> str:
    """
    Check if job title is present
    """
    result = await _async_api_call(f"{BASE_ENDPOINT}/title_check",
                                  {"job_title": job_title, "job_description": job_desc})
    if int(result):
        text_to_display = "This is a clear job title."
        box_job_title_clarity.success(text_to_display, icon="✅")
    else:
        alternative_titles = await _async_api_call(f"{BASE_ENDPOINT}/alt_titles",
                                                   {"job_title": job_title, "job_description": job_desc})
        alternative_titles = json.loads(alternative_titles)
        alternative_titles_numbered = [f"\n\n {num+1}. {alt_title}" for num, alt_title in enumerate(alternative_titles)]
        alternative_titles_numbered_text = ''.join(alternative_titles_numbered)
        text_to_display = f"You may want to consider these alternative titles: \n {alternative_titles_numbered_text}"
        box_job_title_clarity.warning(text_to_display, icon="📣")

    expander_job_title_clarity.update(label="**Is my job title clear?**",
                                      expanded=True,
                                      state="complete")

    st.toast("Job title has been checked!", icon="🎉")

    return text_to_display

async def check_content(box_job_desc_content_present: DeltaGenerator,
                        box_job_desc_content_afi: DeltaGenerator,
                        expander_job_desc_content: DeltaGenerator,
                        job_title: str, 
                        job_desc: str) -> tuple[str, str]:
    """
    Check if job description is present
    """
    result = await _async_api_call(f"{BASE_ENDPOINT}/positive_content_check",
                                  {"job_title": job_title, "job_description": job_desc})
    
    result = json.loads(result)

    present_text = "Good job - your JD contains the following: \n \n"
    missing_text = "You may want to add or make clearer the following: \n \n"

    for _, item in enumerate(result.keys()):
        if result[item]:
            item_formatted = item.replace("_", " ").capitalize()
            present_text += f"\n - {item_formatted}"
        else:
            item_formatted = item.replace("_", " ").capitalize()
            missing_text += f"\n - {item_formatted}"

    result = await _async_api_call(f"{BASE_ENDPOINT}/negative_content_check",
                                  {"job_title": job_title, "job_description": job_desc})
        
    result = json.loads(result)

    negative_text = "You may want to consider removing the following: "

    for count, item in enumerate(result.keys()):
        if result[item]:
            item_formatted = item.replace("_", " ").capitalize()
            negative_text += f"\n - {item_formatted}"

    box_job_desc_content_present.success(present_text)
    area_for_improvement_text = f"**Areas for Improvement:** \n \n {missing_text} \n \n {negative_text}"
    if area_for_improvement_text != "⚠️ **Areas for Improvement:** \n \n {missing_text} \n \n {negative_text}":
        box_job_desc_content_afi.warning(area_for_improvement_text)

    expander_job_desc_content.update(label="**Is there sufficient info in my JD?**",
                                      expanded=True,
                                      state="complete")
    
    st.toast("Job description content been checked!", icon="🎉")
    
    return present_text, area_for_improvement_text

async def get_skills(box_skills: DeltaGenerator,
                     expander_skills: DeltaGenerator,
                     ssoc: int) -> str:
    """
    Get skills
    """
    result = await _async_api_call("https://njsi.herokuapp.com/api/v1/whoami",
                                   {"input_dict": {"current_SSOC": ssoc}})
    
    result = json.loads(result)
    differentiator_skills = result["results"][0]['differentiator_skills']
    differentiator_skills_top_3 = differentiator_skills[:3]

    numbered_skills = [str(num+1) + '. ' + skill.capitalize() + ' \n' for num, skill in enumerate(differentiator_skills_top_3)]
    text_to_display = ''.join(numbered_skills)

    box_skills.info(text_to_display)

    expander_skills.update(label="**What additional skills should I emphasize?**",
                            expanded=True,
                            state="complete")

    st.toast("Relevant skills have been suggested!", icon="🎉")

    return text_to_display

async def generate_recommendations(box_job_design_suggestions: DeltaGenerator,
                                   expander_job_design_suggestion: DeltaGenerator,
                                   title: str,
                                   description: str) -> str:
    """
    Generate recommendations
    """
    stream = _async_api_call_streaming(f"{BASE_ENDPOINT}/job_design_suggestions",
                                       {"job_title": title, "job_description": description,  "groq": False})
    
    text_to_display = "**💡 Job Design Suggestions:** \n \n"

    async for chunk in stream:
        chunk = chunk.decode('utf-8')
        for char in chunk:
            text_to_display += char
            box_job_design_suggestions.info(text_to_display)
            time.sleep(0.01)

    expander_job_design_suggestion.update(label="**How can I re-design my job?**",
                                          expanded=True,
                                          state="complete")

    st.toast("Job design suggestions have been provided!", icon="🎉")

    return text_to_display
        
async def generate_ai_version(box_ai_written_job_desc: DeltaGenerator,
                              expander_ai_written_job_desc: DeltaGenerator,
                              job_title: str,
                              job_desc: str) -> str:
    """
    Generate AI version
    """
    stream = _async_api_call_streaming(f"{BASE_ENDPOINT}/rewrite_jd",
                                       {"job_title": job_title, "job_description": job_desc, "groq": False})
    
    text_to_display = ""

    async for chunk in stream:
        chunk = chunk.decode('utf-8')
        for char in chunk:
            text_to_display += char
            time.sleep(0.01)
            box_ai_written_job_desc.info(text_to_display)
        
    expander_ai_written_job_desc.update(label="**AI-Written JD**",
                                        expanded=True,
                                        state="complete")

    return text_to_display


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

def write_to_google_sheet(data: Any) -> None:
    """
    Add to GSheet
    """
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(st.secrets["GCP_SERVICE_ACCOUNT"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(st.secrets["PRIVATE_GSHEETS_URL"])
    worksheet = sh.get_worksheet(0)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([current_time, data])
