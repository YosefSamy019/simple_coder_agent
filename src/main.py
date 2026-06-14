from src.view.agent_loop import is_goal_achieved, call_model
from src.view.chat_view import build_chat, build_messages
from src.view.init_view import init
from src.view.sidebar_view import build_sidebar
from tools import *


def main():
    init()
    build_sidebar()
    build_chat()
    build_messages()

    if is_goal_achieved():
        st.session_state[AGENT_STATUS] = AgentStatus.STOPPED

    if st.session_state.get(AGENT_STATUS) == AgentStatus.RUNNING:
        call_model()
        st.rerun()


if __name__ == "__main__":
    main()
