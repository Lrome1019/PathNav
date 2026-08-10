import streamlit as st

st.set_page_config(page_title="PathNav",page_icon="🧭",layout="wide")
st.title("🧭PathNav")

from utils.theme import inject_css

inject_css()

with st.sidebar:
    st.markdown(
        "PathNav is a prototype for a tool that helps students navigate their "
        "academic journey, accommodations, ask policy questions, get "
        "step-by-step guidance, and draft accommodation emails, all in one place."
    )
    st.markdown("Made by the [PathNav team](https://pathnav.app) at the.")
