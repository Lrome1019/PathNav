import streamlit as st

st.set_page_config(page_title="PathNav",page_icon="🧭",layout="wide")
st.title("🧭PathNav")

from utils.theme import inject_css
from utils.loader import load

init_session_state = load("utils/session state.py").init_session_state
APIClient = load("utils/api client.py").APIClient

init_session_state()
api_client = APIClient()
inject_css()

with st.sidebar:
    st.markdown(
        "PathNav is a prototype for a tool that helps students navigate their "
        "academic journey, accommodations, ask policy questions, get "
        "step-by-step guidance, and draft accommodation emails, all in one place."
    )
    st.markdown("Made by the [PathNav team](https://pathnav.app) at the.")
