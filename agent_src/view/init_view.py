import streamlit as st

from agent_src.models.models import *
from agent_src.values.const import *
from agent_src.values.prompts import MAIN_SYS_MSG


def init():
    st.set_page_config(
        page_title="My Simple Coder Agent 🤖",
        layout="wide",
    )

    st.session_state.setdefault(URL_KEY, 'https://92f3-34-6-166-144.ngrok-free.app')
    st.session_state.setdefault(END_POINT_KEY, '/v1')
    st.session_state.setdefault(CALLS_COUNTER, 0)
    st.session_state.setdefault(FILES_SYSTEM, [])
    st.session_state.setdefault(API_WARNING, True)

    st.session_state.setdefault(AGENT_STATUS, AgentStatus.STOPPED)

    st.session_state.setdefault(MSGS_KEY, [
        MAIN_SYS_MSG
    ])
