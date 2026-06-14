import streamlit as st

from agent_src.models.models import *
from agent_src.values.const import *
from agent_src.view.common import add_message


def handle_input():
    prompt = st.session_state.get(CHAT_KEY)

    if not prompt:
        return

    add_message(UserChatMsg(content=prompt))

    st.session_state[AGENT_STATUS] = AgentStatus.RUNNING


def build_chat():
    st.title(f"🤖 My Simple Coder Agent")

    st.markdown(f'N Model Calls: {st.session_state[CALLS_COUNTER]}')

    st.chat_input(
        "Ask the agent...",
        key=CHAT_KEY,
        on_submit=handle_input,
    )


def build_messages():
    for i, msg in enumerate(st.session_state[MSGS_KEY]):
        is_this_last = i == len(st.session_state[MSGS_KEY]) - 1

        if isinstance(msg, UserChatMsg):
            with st.chat_message(
                    name='human',
                    avatar="👤"
            ):
                st.markdown(msg.content)

        elif isinstance(msg, AssistantChatMsg):
            if len(msg.content) > 0:
                with st.chat_message(
                        name='ai',
                        avatar="🤖"
                ):
                    st.markdown(msg.content)

            if len(msg.reasoning) > 0 and is_this_last and st.session_state[AGENT_STATUS] == AgentStatus.RUNNING:
                with st.chat_message(
                        name='ai',
                        avatar="💡"
                ):
                    st.markdown('```Reasoning```')
                    st.markdown(msg.reasoning)

        elif isinstance(msg, SystemChatMsg):
            with st.expander(label=f'⚙️ System Message'):
                st.markdown(msg.content)


        elif isinstance(msg, ToolCallChatMsg):
            with st.expander(label=f'🔨 ```{msg.function_name}``` {msg.result[:150]}'):
                st.markdown(f"```call id:``` {msg.tool_call_id}")
                st.markdown(f"```function:``` {msg.function_name}")
                st.markdown(f"```args:``` {msg.function_arguments}")
                st.divider()
                st.markdown(f"```result:```")
                st.markdown(f"{msg.result}")
        else:
            st.error(f"Unknown message, type{type(msg)}")
