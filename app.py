"""
app.py
"""
import streamlit as st

import tab_add_jd
import tab_feedback
import tab_rewrite_jd
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
    tab_add_jd.generate_view()

with tab2:
    tab_feedback.generate_view()

with tab3:
    tab_rewrite_jd.generate_view()
