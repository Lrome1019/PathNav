"""
policy_qa_tab.py — "Policy Q&A" tab

Lets a student ask a free-text question about accommodation rights/policy
and get a plain-language answer. Not part of the original CRC cards, but
follows the same shape as the rest of the app: the frontend collects
input and calls APIClient; the Backend/API teammate will eventually swap
APIClient.get_policy_answer()'s internals for a real Claude API call.

Owner: Laura (Frontend 1)
"""

import streamlit as st

from utils.loader import load

EXAMPLE_QUESTIONS = load("utils/sample data.py").EXAMPLE_QUESTIONS


def render(api_client) -> None:
    st.subheader("Ask About Your Accommodation Rights")
    st.write(
        "Get plain-language answers to questions about disability accommodation "
        "policy, your rights under the ADA/Section 504, and university procedures."
    )

    # Example questions — clicking one fills the text input via session_state.
    st.markdown("**Example questions:**")
    example_cols = st.columns(len(EXAMPLE_QUESTIONS))
    for col, example in zip(example_cols, EXAMPLE_QUESTIONS):
        with col:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                st.session_state.policy_question = example

    question = st.text_input(
        "Ask a question about your accommodation rights...",
        key="policy_question",
    )

    submit_clicked = st.button("Submit Question", key="submit_policy_question")

    st.markdown("#### Response")
    if submit_clicked and question.strip():
        st.session_state.policy_answer = api_client.get_policy_answer(question)
    elif submit_clicked:
        st.warning("Please enter a question before submitting.")

    answer = st.session_state.policy_answer
    if answer:
        st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="response-box">Your answer will appear here once you submit a question.</div>',
            unsafe_allow_html=True,
        )
