"""
app.py
"""
import streamlit as st

import add_jd_page
import feedback_page
import rewrite_page
from utils.st_utils import (
    initialise_session_states,
    set_app_config,
    set_custom_css
)
from utils.config import (
    APP_TITLE,
    TAB_NAMES
    )

initialise_session_states()
set_app_config()
set_custom_css()

st.subheader(APP_TITLE)

tab1, tab2, tab3 = st.tabs(TAB_NAMES)

with tab1:
    add_jd_page.generate_view()

with tab2:
    feedback_page.generate_view()

with tab3:
    rewrite_page.generate_view()
