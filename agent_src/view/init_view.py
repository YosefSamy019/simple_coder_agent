import streamlit as st

from agent_src.models.models import *
from agent_src.tools import AgentTool
from agent_src.values.const import *


def init():
    st.set_page_config(
        page_title="My Simple Coder Agent 🤖",
        layout="wide",
    )

    st.session_state.setdefault(URL_KEY, 'https://26d7-34-169-186-23.ngrok-free.app')
    st.session_state.setdefault(END_POINT_KEY, '/v1')
    st.session_state.setdefault(CALLS_COUNTER, 0)
    st.session_state.setdefault(FILES_SYSTEM, [])

    st.session_state.setdefault(AGENT_STATUS, AgentStatus.STOPPED)

    st.session_state.setdefault(
        MSGS_KEY, [
            SystemChatMsg(content=f"""
You are a helpful coding assistant. Your goal is to help the user with programming tasks.

You have access to the following tools:
{"\n".join([f"- {x().get_name()}: {x().get_description()}" for x in AgentTool.__subclasses__()])}

For each user request:
1. Understand what the user is trying to accomplish
2. Break down complex tasks into smaller steps
3. Use your tools to gather information about the codebase when needed
4. Implement solutions by writing or modifying code
5. Explain your reasoning and approach
6. Call `deliver_task` when you finish the task

When modifying code, be careful to maintain the existing style and structure. Test your changes when possible.
If you're unsure about something, ask clarifying questions before proceeding.

You must run and test your changes before reporting success.
            """.strip()),
        ]
    )
