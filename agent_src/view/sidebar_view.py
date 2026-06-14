import streamlit as st

from agent_src.models.models import *
from agent_src.tools import get_all_tools_list
from agent_src.values.const import *


def build_sidebar():
    with st.sidebar:
        st.title("⚙️ Settings")

        st.text_input(
            label="API URL",
            key=URL_KEY,
        )

        cols_side_bar_a = st.columns(2)

        cols_side_bar_a[0].text_input(
            label="End Point",
            key=END_POINT_KEY,
        )

        cols_side_bar_a[1].selectbox(
            label="Model",
            key=MODEL_KEY,
            index=0,
            options=[
                "gemma4:e2b",
                "gemma4:12b",
                "qwen2.5:3b"
            ]
        )

        st.divider()

        btn_cols_1 = st.columns(2)
        btn_cols_2 = st.columns(2)

        if btn_cols_1[0].button("Clear Chat"):
            st.session_state[MSGS_KEY] = list(
                filter(
                    lambda x: isinstance(x, SystemChatMsg),
                    st.session_state[MSGS_KEY]
                )
            )
        if btn_cols_1[1].button("Clear Directory"):
            st.session_state[FILES_SYSTEM] = []

        if btn_cols_2[0].button("Show Tools"):
            @st.dialog(title="Tools", width='large')
            def dialog():
                st.write(get_all_tools_list())

            dialog()

        if btn_cols_2[1].button("Show Buffer"):
            @st.dialog(title="Tools", width='large')
            def dialog():
                st.write([
                    m.to_json() for m in st.session_state.get(MSGS_KEY)
                ])

            dialog()

        st.divider()

        st.title("📂 File Explorer")

        render_tree()


@st.dialog("File Viewer", width='large')
def show_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        st.code(content, language=filepath.split(".")[-1])
    except Exception as e:
        st.error(f"Could not open file: {e}")


def render_tree(level=0):
    items = st.session_state[FILES_SYSTEM]

    for item in items:
        cols = st.columns([6, 1, 1])

        indent = "&nbsp;" * level * 4
        cols[0].markdown(
            indent + f"📄 {item}",
            unsafe_allow_html=True,
        )

        with cols[1]:
            with open(item, "rb") as f:
                download_name = item
                if '/' in download_name:
                    download_name = download_name.split('/')[-1]
                st.download_button(
                    "📥",
                    data=f.read(),
                    file_name=download_name,
                    key=f"download_{item}",
                )

        with cols[2]:
            if st.button(
                    "👁",
                    key=f"view_{item}",
                    help="View file",
            ):
                show_file(item)
