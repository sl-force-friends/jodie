"""
tab_feedback.py
"""
import time

import asyncio
import chromadb
# type: ignore
import instructor
import streamlit as st
from openai import AsyncAzureOpenAI, AzureOpenAI
import tab_rewrite_jd

from utils.prompts import (
    TitleCheck,
    AlternativeTitles,
    PositiveContentCheck,
    NegativeContentCheck,
    JD_SUGGESTION_SYSTEM_MESSAGE
    )
from utils.config import (
    API_KEY,
    AZURE_ENDPOINT,
    API_VERSION
    )

client = instructor.apatch(AsyncAzureOpenAI(api_key=API_KEY,
                                            azure_endpoint=AZURE_ENDPOINT,
                                            api_version=API_VERSION))

sync_client = AzureOpenAI(api_key=API_KEY,
                          azure_endpoint=AZURE_ENDPOINT,
                          api_version=API_VERSION)

db_client = chromadb.PersistentClient()
db_collection = db_client.get_collection(name="ICT_SS")

def generate_view():
    """
    Generate the view for the feedback tab
    """
    # if (st.session_state['user_title'] is None) and (st.session_state['user_desc'] is None):
    #     st.warning("Please enter your job description first", icon="⚠️")
    #     return None
    
    # button = st.empty()

    # # if button.button("Generate Feedback"):
    # button.empty()
    row1 = st.container()
    row1.markdown("""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px;">
        <strong>Title Check</strong>
    </div>
    """,
    unsafe_allow_html=True)
    title_box = row1.empty()
    row1.markdown("""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px;">
        <strong>Content Check</strong>
    </div>
    """,
    unsafe_allow_html=True)
    present_content_box = row1.empty()
    missing_content_box = row1.empty()
    to_remove_content_box = row1.empty()
    row2 = st.container()
    row2.markdown("""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'avenir next', avenir, helvetica, 'helvetica neue', ubuntu, roboto, noto, 'segoe ui', arial, sans-serif; color: #cf008a; font-size: 20px;; margin: 2px;">
        <strong>Job Design Suggestions</strong>
    </div>
    """,
    unsafe_allow_html=True)
    # row2.subheader("3. Job Design Suggestions")
    recommendations_box = row2.empty()
    asyncio.run(main(title_box, present_content_box, missing_content_box, to_remove_content_box, recommendations_box, st.session_state["user_title"], st.session_state["user_desc"]))
    st.session_state["generated_ai_feedback"] = True
    # tab_rewrite_jd.generate_view()

        # st.subheader("4. Feedback")
        # st.info("**Scoring System:** 1 = Not useful, 5 = Very useful")
        # st.session_state["rating_ai_feedback_useful"] = st.radio("How useful was the feedback?", options=["1", "2", "3", "4", "5"], horizontal=True, index=None)
        # st.session_state["rating_ai_feedback_accurate"] = st.radio("How accurate was the feedback?", options=["1", "2", "3", "4", "5"], horizontal=True, index=None)
        # st.session_state["rating_ai_feedback_others"] = st.text_area("Any other feedback?", height=100)

        # if st.button("Submit"):
        #     if st.session_state["rating_ai_feedback_useful"] is None and st.session_state["rating_ai_feedback_accurate"] is None:
        #         st.warning("Please fill in the feedback ratings", icon="⚠️")
        #     else:
        #         st.balloons()
               
async def main(box1, box2, box3, box4, box5, title, description):
    """
    Asynchronous function to run the main logic
    """
    results = await asyncio.gather(
        check_job_title(box1, title, description),
        check_positive_content(box2, box3, title, description),
        check_negative_content(box4, title, description),
        generate_recommendations(box5, title, description)
    )

    st.session_state["ai_feedback"] = results

async def check_job_title(box, title, description):
    """
    Checks the job title
    """
    box.info("Generating AI feedback...")
    response = await client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=[{"role": "user", 
                   "content": f"Check if this job description for {title} matches the title. Else, provide alternative suggestions. Here is the description: {description}"}],
        response_model=TitleCheck,
        max_retries=5,
        seed=0,
        temperature=0
    )

    if response.does_title_match:
        box.success("Job Title is clear ✅")
    else:
        response = await client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=[{"role": "user", 
                   "content": f"Provide alternative job titles for this job description delimited by ###. Do not use {title}. Here is the job description: ### {description}"}],
        response_model=AlternativeTitles,
        max_retries=5,
        seed=0,
        temperature=0
        )
        box.info(f"You may want to consider these alternative job titles: {response.alternative_titles}")

    return response

async def check_positive_content(boxA, boxB, title, description):
    """
    Checks the job title
    """
    boxA.info("Generating AI feedback...")
    boxB.info("Generating AI feedback...")
    response = await client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=[{"role": "user", 
                   "content": f"Check the contents of this job description for {title}: {description}"}],
        response_model=PositiveContentCheck,
        max_retries=5,
        seed=0,
        temperature=0,
    )
    box1_text = "**Present in JD ✅** \n \n"
    for field in response.__fields__:
        if getattr(response, field):
            box1_text += f"- {field.replace('_', ' ').capitalize()} \n"

    box2_text = "**Missing in JD ❓** \n \n"
    for field in response.__fields__:
        if not getattr(response, field):
            box2_text += f"- {field.replace('_', ' ').capitalize()} \n"

    if box1_text != "**Present in JD ✅** \n \n":
        boxA.success(box1_text)
    else:
        boxA.empty()

    if box2_text != "**Missing in JD ❓** \n \n":
        boxB.warning(box2_text)
    else:
        boxB.empty()

    return response

async def check_negative_content(box, title, description):
    """
    Checks the job title
    """
    box.info("Generating AI feedback...")
    response = await client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=[{"role": "user", 
                   "content": f"Check the contents of this job description for {title}: {description}"}],
        response_model=NegativeContentCheck,
        max_retries=5,
        seed=0,
        temperature=0,
    )
    text = "**You may want to remove:**"
    if response.required_years_of_experience:
        text += "\n \n - 'years of experience' requirement"

    if response.required_formal_education:
        text += "\n \n- 'formal education credentials' requirement"

    if text != "**You may want to remove:**":
        box.empty()
        box.warning(text)
    else:
        box.empty()

    return response

async def generate_recommendations(box, title, description):
    """
    Checks the job title
    """

    box.info("Generating AI feedback...")
    doc_extracts = _get_relevant_chunks(title, description)

    prompt = f"""
        The job description for {title} is delimited by "###", and report extracts delimited by "$$$"

        ###
        {description}

        $$$
        {doc_extracts[0]}
        {doc_extracts[1]}
        {doc_extracts[2]}
        {doc_extracts[3]}
        {doc_extracts[4]}
        """

    stream = await client.chat.completions.create(
        model="gpt-4-32k",
        messages=[{"role": "system", "content": JD_SUGGESTION_SYSTEM_MESSAGE},
                  {"role": "user", "content": prompt}],
        frequency_penalty=1,
        max_tokens=500,
        seed=0,
        temperature=0,
        stream=True
    )

    box.empty()
    recommendations = "**Feedback:** \n \n"
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            text = chunk.choices[0].delta.content
            for character in text:
                recommendations += character
                box.info(recommendations)
                time.sleep(0.01)

    return {"documents": doc_extracts, "recommendations": recommendations}

def _get_relevant_chunks(title, description):
    results = db_collection.query(query_embeddings=_get_embedding(title+description), n_results = 5)
    documents = results['documents'][0]
    return documents
 

def _get_embedding(text):
    embeddings = sync_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    return embeddings.data[0].embedding
    




    # streamed_text = "**Job Title Clarity:** \n \n "
    # async for chunk in stream:
    #     chunk_content = chunk.choices[0].delta.content
    #     if chunk_content is not None:
    #         streamed_text = streamed_text + chunk_content
    #         box.success(streamed_text)


# async def check_keywords(box, title, description):
#     """
#     Checks the keywords
#     """
#     stream = await client.chat.completions.create(
#         model="gpt-35-turbo-16k",
#         messages=[{"role": "system", "content": CHECK_KEYWORDS_SYS_MSG},
#                   {"role": "user", "content": f"<TITLE> {title} </TITLE> \n <DESCRIPTION> {description} </DESCRIPTION>"}],
#         seed=0,
#         temperature=0,
#         stream=True
#     )
#     streamed_text = "**Additional keywords to add:** \n \n "
#     async for chunk in stream:
#         chunk_content = chunk.choices[0].delta.content
#         if chunk_content is not None:
#             streamed_text = streamed_text + chunk_content
#             box.success(streamed_text)
