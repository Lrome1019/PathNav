import streamlit as st

st.set_page_config(page_title="PathNav", page_icon=":compass:", layout="wide")
st.title("PathNav")

from utils.theme import inject_css
from utils.loader import load

init_session_state = load("utils/session state.py").init_session_state
APIClient = load("utils/api client.py").APIClient

scanner_tab = load("components/scanner tab.py")
toc_tab = load("components/toc tab.py")
email_draft_tab = load("components/email draft tab.py")
policy_qa_tab = load("components/policy qa tab.py")
navigator_tab = load("components/navigator tab.py")

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

scanner, toc, email_draft, policy_qa, navigator = st.tabs(
    [
        "Syllabus Scanner",
        "Table of Contents",
        "Email Draft",
        "Policy Q&A",
        "Navigator",
    ]
)

with scanner:
    scanner_tab.render(api_client)
with toc:
    toc_tab.render(api_client)
with email_draft:
    email_draft_tab.render(api_client)
with policy_qa:
    policy_qa_tab.render(api_client)
with navigator:
    navigator_tab.render()
