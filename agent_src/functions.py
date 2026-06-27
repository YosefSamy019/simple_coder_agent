from typing import List

from agent_src.models.models import ChatMsg
import streamlit as st

from agent_src.values.const import MSGS_KEY
from agent_src.values.prompts import MAIN_SYS_MSG


def clear_msgs_buffer():
    st.session_state[MSGS_KEY] = [
        MAIN_SYS_MSG
    ]


def get_active_chat_msgs() -> List[ChatMsg]:
    return list(
        filter(
            lambda msg: msg.expired == False,
            st.session_state[MSGS_KEY]
        )
    )

