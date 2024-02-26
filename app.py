"""
app.py
"""
# For hosting on streamlit community cloud
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except:
    pass

import streamlit as st

import tab_add_jd
import tab_feedback
import tab_rewrite_jd

from utils.st_utils import (
    disclaimer,
    initialise_session_states,
    last_update,
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

if st.session_state["read_terms"] is False:
    last_update()
    disclaimer()
    if st.button("Accept"):
        st.session_state["read_terms"] = True
        st.rerun()

else:
    st.subheader(APP_TITLE)

    # tab1, tab2, tab3 = st.tabs(TAB_NAMES)

    # with tab1:
    #     tab_add_jd.generate_view()

    # with tab2:
    #     tab_feedback.generate_view()

    # with tab3:
    #     tab_rewrite_jd.generate_view()

    st.write(TAB_NAMES[0])
    tab_add_jd.generate_view()

    # st.write(TAB_NAMES[1])
    # tab_feedback.generate_view()

    tab_rewrite_jd.generate_view()





