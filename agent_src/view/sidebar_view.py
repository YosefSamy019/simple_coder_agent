import streamlit as st

from agent_src.models.models import *
from agent_src.tools import get_all_tools_list
from agent_src.values.const import *


def _disable_warning():
    st.session_state[API_WARNING] = False


def build_sidebar(
        clear_chat_func,
):
    with st.sidebar:
        st.title("⚙️ Settings")

        st.text_input(
            label="API URL",
            key=URL_KEY,
            on_change=_disable_warning
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
                "gemma4:12b"
            ]
        )

        st.divider()

        btn_cols_1 = st.columns(2)
        btn_cols_2 = st.columns(2)

        if btn_cols_1[0].button("Clear Chat", width='stretch') and clear_chat_func:
            clear_chat_func()

        if btn_cols_1[1].button("Clear Directory", width='stretch'):
            st.session_state[FILES_SYSTEM] = []

        if btn_cols_2[0].button("Show Tools", width='stretch'):
            @st.dialog(title="Tools", width='large')
            def dialog():
                st.write(get_all_tools_list())

            dialog()

        if btn_cols_2[1].button("Show Buffer", width='stretch'):
            @st.dialog(title="Tools", width='large')
            def dialog():
                st.write([
                    m.to_json() for m in st.session_state.get(MSGS_KEY)
                ])

            dialog()

        st.divider()

        st.title("📂 File Explorer")

        uploaded_files = st.file_uploader(
            label="Upload Files",
            accept_multiple_files=True,
            type=[
                "txt",
                "md",
                "csv",
                "json",
                "xml",
                "yaml",
                "yml",
                "ini",
                "cfg",
                "conf",
                "log",
                "py",
                "js",
                "ts",
                "java",
                "c",
                "cpp",
                "cc",
                "h",
                "hpp",
                "cs",
                "go",
                "rs",
                "sh",
                "bat",
                "ps1",
                "html",
                "css",
                "sql",
                "toml",
                "tex",
                "rtf",
            ],
        )

        if uploaded_files:
            handle_uploaded_file(uploaded_files)

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


def handle_uploaded_file(files_list):
    for file in files_list:
        data = file.read()
        total_path = file.name
        file_name = file.name

        with open(f'{total_path}', "wb") as f:
            f.write(data)

        files = st.session_state.get(
            FILES_SYSTEM,
            []
        )

        if total_path not in files:
            files.append(total_path)

        st.session_state[FILES_SYSTEM] = files
