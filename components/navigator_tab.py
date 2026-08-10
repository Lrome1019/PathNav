"""
navigator_tab.py — "Navigator" tab

Step-by-step guidance for common accommodation situations: request an
accommodation, a professor denied one, a new diagnosis, or needing an
extension. Dropdown selects a situation; Next/Back walk through
NAVIGATOR_GUIDES one step at a time.

Owner: Frontend Teammate
(scaffolded by Laura so the team has a working starting point — please
make this your own! natural next steps: swap NAVIGATOR_GUIDES for
API-generated steps, add a "draft an email about this" handoff into the
Email Draft tab, add richer step content like links/checklists.)
"""

import streamlit as st

from utils.sample_data import NAVIGATOR_GUIDES


def render() -> None:
    st.subheader("Step-by-Step Navigator")
    st.write("Select a situation below and follow the guided steps.")

    situation = st.selectbox(
        "What do you need help with today?",
        options=list(NAVIGATOR_GUIDES.keys()),
        key="navigator_situation_select",
    )

    # Reset the step index whenever the selected situation changes, so
    # switching topics always starts back at step 1.
    if st.session_state.nav_situation != situation:
        st.session_state.nav_step_index = 0
        st.session_state.nav_situation = situation

    steps = NAVIGATOR_GUIDES[situation]
    step_index = st.session_state.nav_step_index
    total_steps = len(steps)

    st.markdown(
        f"""
        <div class="step-card">
            <h4>Step {step_index + 1} of {total_steps}</h4>
            <p style="font-size: 1.05rem;">{steps[step_index]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress((step_index + 1) / total_steps)

    back_col, next_col = st.columns(2)
    with back_col:
        if st.button("⬅ Back", disabled=(step_index == 0), use_container_width=True):
            st.session_state.nav_step_index = max(0, step_index - 1)
            st.rerun()
    with next_col:
        if st.button("Next ➡", disabled=(step_index == total_steps - 1), use_container_width=True):
            st.session_state.nav_step_index = min(total_steps - 1, step_index + 1)
            st.rerun()
