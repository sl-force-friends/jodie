"""
tab_rewrite_jd.py
"""
import time
import streamlit as st
import difflib
from openai import AzureOpenAI

import tab_feedback

from utils.prompts import REWRITE_SYSTEM_MESSAGE
from typing import Iterable
from utils.config import (
    API_KEY,
    AZURE_ENDPOINT,
    API_VERSION
    )
from utils.config import (
    APP_TITLE,
    # TAB_NAMES
    )

client = AzureOpenAI(api_key=API_KEY,
                     azure_endpoint=AZURE_ENDPOINT,
                     api_version=API_VERSION)

def generate_view():
    """
    Generate the view for the re-write tab
    """

    if (st.session_state['user_title'] is None) and (st.session_state['user_desc'] is None):
        st.warning("Please enter your job description first", icon="⚠️")
        return None
    
    # if not st.session_state["generated_ai_feedback"]:
    #     st.warning("Please generate the AI feedback first", icon="⚠️")
    #     return None

    button = st.empty()

    if button.button("Rewrite with AI", use_container_width=True, type='primary'):
        button.empty()
        tab_feedback.generate_view()
        st.markdown("""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px;">
            <strong>Job Description Rewrite</strong>
        </div>
        """,
        unsafe_allow_html=True)
        # st.subheader("Job Description Rewrite")
        _rewrite(st.session_state["user_title"], st.session_state["user_desc"])

        with st.expander("Copy to Clipboard"):
            st.write(f" ``` {_add_line_breaks(st.session_state['ai_rewrite'])}")

        diff_changes = highlight_changes(st.session_state["user_desc"], st.session_state["ai_rewrite"])

        st.markdown(diff_changes, unsafe_allow_html=True)

        

        # RATING
        # st.subheader("Feedback")
        # st.info("**Scoring System:** 1 = Not useful, 5 = Very useful")
        # st.session_state["rating_ai_rewrite_useful"] = st.radio("How useful was the re-written JD?", options=["1", "2", "3", "4", "5"], horizontal=True, index=None)
        # st.session_state["rating_ai_rewrite_accurate"] = st.radio("How accurate was the re-written JD?", options=["1", "2", "3", "4", "5"], horizontal=True, index=None)
        # st.session_state["rating_ai_rewrite_others"] = st.text_area("Any other comments for the re-written JD?", height=100)

def _rewrite(title, description):
    re_write_jd = st.container()
    with re_write_jd:
        st.write("Generating AI response")
    # re_write_jd.info("Generating AI version...")
    stream = client.chat.completions.create(
        model="gpt-4-32k",
        messages=[{"role": "system", "content": REWRITE_SYSTEM_MESSAGE},
                  {"role": "user", "content": f"{title}: {description}."}],
        seed=0,
        temperature=0,
        frequency_penalty=1,
        stream=True
    )
    streamed_text = ""
    total_chars = 0

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            for character in chunk_content:
                streamed_text += character
                streamed_text = streamed_text.replace("```", "")
                # streamed_text = _add_line_breaks(streamed_text)
                time.sleep(0.01)

    st.session_state["ai_rewrite"] = streamed_text
    with re_write_jd:
        st.write(f"""
                {streamed_text}
                """)

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

def highlight_changes(original_text, edited_text):
    # Split the texts into lines for comparison
    original_lines = original_text.splitlines()
    edited_lines = edited_text.splitlines()
    
    # Get the differences between the original and edited texts
    differ = difflib.Differ()
    diff = list(differ.compare(original_lines, edited_lines))
    
    # Create HTML to highlight changes
    highlighted_lines = []
    for line in diff:
        if line.startswith('+'):
            # Addition: highlight in green
            highlighted_lines.append(f'<span style="color:green">{line[2:]}</span>')
        elif line.startswith('-'):
            # Deletion: highlight in red
            highlighted_lines.append(f'<span style="color:grey">{line[2:]}</span>')
        elif line.startswith('?'):
            # Common line: no highlight
            highlighted_lines.append(line[2:])
        else:
            # Common line: no highlight
            highlighted_lines.append(line)
    
    # Join the lines back together
    highlighted_text = '\n'.join(highlighted_lines)
    
    return highlighted_text