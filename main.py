import shutil

from const import *
import asyncio
from openai import OpenAI
from pathlib import Path

from models import SystemChatMsg, ChatMsg, UserChatMsg, AssistantChatMsg, ToolCallChatMsg, AgentStatus
from tools import *


# =====================
# State Management
# =====================

def init():
    st.set_page_config(
        page_title="My Simple Coder Agent 🤖",
        layout="wide",
    )

    st.session_state.setdefault(URL_KEY, 'https://f169-136-117-78-58.ngrok-free.app')
    st.session_state.setdefault(END_POINT_KEY, '/v1')

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


def add_message(msg: ChatMsg):
    st.session_state[MSGS_KEY].append(msg)


# =====================
# Sidebar
# =====================

def build_sidebar():
    with st.sidebar:
        st.title("⚙️ Settings")

        st.text_input(
            label="API URL",
            key=URL_KEY,
        )

        st.text_input(
            label="End Point",
            key=END_POINT_KEY,
        )

        st.selectbox(
            label="Model",
            key=MODEL_KEY,
            index=0,
            options=[
                "gemma4:e2b",
                "qwen2.5:3b"
            ]
        )

        st.divider()

        btn_cols = st.columns(3)

        if btn_cols[0].button("Clear Chat"):
            st.session_state[MSGS_KEY] = list(
                filter(
                    lambda x: isinstance(x, SystemChatMsg),
                    st.session_state[MSGS_KEY]
                )
            )
        if btn_cols[1].button("Clear Directory"):
            directory = Path(AgentTool.WORKING_DIR)

            for item in directory.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        if btn_cols[2].button("Show Tools"):
            @st.dialog(title="Tools", width='large')
            def dialog():
                st.write(get_all_tools_list())

            dialog()

        st.divider()

        st.title("📂 File Explorer")

        render_tree(Path(AgentTool.WORKING_DIR))


@st.dialog("File Viewer", width='large')
def show_file(filepath: Path):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        st.code(content, language=filepath.suffix.lstrip("."))
    except Exception as e:
        st.error(f"Could not open file: {e}")


def render_tree(path: Path, level=0):
    items = sorted(
        path.iterdir(),
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for item in items:
        if item.is_dir():
            st.markdown("&nbsp;" * level * 4 + f"📁 **{item.name}**",
                        unsafe_allow_html=True)
            render_tree(item, level + 1)

        else:
            cols = st.columns([6, 1, 1])

            indent = "&nbsp;" * level * 4
            cols[0].markdown(
                indent + f"📄 {item.name}",
                unsafe_allow_html=True,
            )

            with cols[1]:
                with open(item, "rb") as f:
                    st.download_button(
                        "📥",
                        data=f.read(),
                        file_name=item.name,
                        key=f"download_{item}",
                    )

            with cols[2]:
                if st.button(
                        "👁",
                        key=f"view_{item}",
                        help="View file",
                ):
                    show_file(item)


# =====================
# Chat
# =====================

def handle_input():
    prompt = st.session_state.get(CHAT_KEY)

    if not prompt:
        return

    add_message(UserChatMsg(content=prompt))

    st.session_state[AGENT_STATUS] = AgentStatus.RUNNING


def build_chat():
    st.title("🤖 My Simple Coder Agent")

    st.chat_input(
        "Ask the agent...",
        key=CHAT_KEY,
        on_submit=handle_input,
    )


def build_messages():
    for msg in st.session_state[MSGS_KEY]:
        if isinstance(msg, UserChatMsg):
            with st.chat_message(
                    name='human',
                    avatar="👤"
            ):
                st.markdown(msg.content)

        elif isinstance(msg, AssistantChatMsg):
            with st.chat_message(
                    name='ai',
                    avatar="🤖"
            ):
                st.markdown(msg.content)

        elif isinstance(msg, SystemChatMsg):
            with st.container(border=True):
                # st.markdown('⚙️ System Message: ```Hidden```')
                st.markdown(msg.content)


        elif isinstance(msg, ToolCallChatMsg):
            with st.expander(label=f'💻 {msg.function_name} {msg.result[:300]}'):
                st.markdown(f"call id: {msg.tool_call_id}")
                st.markdown(f"function: {msg.function_name}")
                st.markdown(f"args: {msg.function_arguments}")
                st.divider()
                st.markdown(f"result:")
                st.markdown(f"{msg.result}")
        else:
            st.error(f"Unknown message, type{type(msg)}")


def is_goal_achieved() -> bool:
    if len(st.session_state.get(MSGS_KEY)) > 0:
        last_msg = st.session_state.get(MSGS_KEY)[-1]

        if isinstance(last_msg, AssistantChatMsg):
            if len(last_msg.tool_calls) == 0:
                return True

    return False


def call_model():
    try:
        client = OpenAI(
            base_url=st.session_state.get(URL_KEY) + st.session_state.get(END_POINT_KEY),
            api_key='111'
        )

        completion = client.chat.completions.create(
            model=st.session_state.get(MODEL_KEY),
            messages=[
                m.to_json() for m in st.session_state.get(MSGS_KEY)
            ],
            tools=get_all_tools_list(),
        )

        assistant_msg = AssistantChatMsg(
            content=completion.choices[0].message.content,
            tool_calls=completion.choices[0].message.tool_calls,
        )

        if len(assistant_msg.content.strip()) > 0:
            add_message(assistant_msg)

        for tool_call_json in assistant_msg.tool_calls:
            function_name = tool_call_json.function.name
            function_arguments = json.loads(tool_call_json.function.arguments)
            tool_call_id = tool_call_json.id

            result = "Tool Not Found"

            for tool_class in AgentTool.__subclasses__():
                tool_obj = tool_class()
                if tool_obj.get_name() == function_name:
                    result = tool_obj.execute(parameters=function_arguments)
                    break

            add_message(
                ToolCallChatMsg(
                    tool_call_id=tool_call_id,
                    function_name=function_name,
                    function_arguments=function_arguments,
                    result=result
                )
            )

    except Exception as e:
        # raise e
        st.error(e)

    finally:
        pass


# =====================
# Main
# =====================

def main():
    os.makedirs(AgentTool.WORKING_DIR, exist_ok=True)

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
