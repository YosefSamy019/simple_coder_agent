from src.models.models import ChatMsg
from src.values.const import MSGS_KEY
import streamlit as st

def add_message(msg: ChatMsg):
    st.session_state[MSGS_KEY].append(msg)
