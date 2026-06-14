from agent_src.models.models import AgentStatus
from agent_src.values.const import AGENT_STATUS
from agent_src.view.agent_loop import is_goal_achieved, call_model
from agent_src.view.chat_view import build_chat, build_messages
from agent_src.view.init_view import init
from agent_src.view.sidebar_view import build_sidebar
import streamlit as st


def main():
    init()
    build_sidebar()
    build_chat()
    build_messages()

    if is_goal_achieved() and st.session_state[AGENT_STATUS] == AgentStatus.RUNNING:
        st.session_state[AGENT_STATUS] = AgentStatus.STOPPED
        st.rerun()

    if st.session_state.get(AGENT_STATUS) == AgentStatus.RUNNING:
        call_model()
        st.rerun()


if __name__ == "__main__":
    main()
