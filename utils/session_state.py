import streamlit as st

def init_session_state() -> None:
    """Sets default values for every st.session_state key the app uses.
        Called once from app.py, before any tab renders, so every tab can
        safely assume these keys already exist. """

defaults = {
       "courses": [],
        "scan_job_status": None,

        #--- Policy QA tab ---
        "policy_qa_question": "",
        "policy_answer": None,
        "policy_documents": [],

        "generated_email": None,

        ## Aamr Build from here ---
    }

for key, value in defaults.items():
    st.session_state[key] = value