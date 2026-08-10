"""
PathNav
-------
An AI-powered assistant that helps college students navigate university
disability services — syllabus scanning, policy Q&A, guided next steps,
and accommodation email drafting in one place. Built for the Pathfinders
Challenge.

This file is the app shell only: page config, global theme, sidebar, and
tab routing. Each tab's actual content lives in components/, and shared
plumbing (session state, the placeholder API client, sample data) lives
in utils/ — see PATHNAV_TEAM_GUIDE.md for how the team splits this up.

Owner: Laura (Frontend 1) — DashboardApp / NavigationBar
"""

import streamlit as st

from components import scanner_tab, policy_qa_tab, email_draft_tab, navigator_tab, toc_tab
from utils.api_client import APIClient
from utils.session_state import init_session_state
from utils.theme import inject_css

# ---------------------------------------------------------------------------
# PAGE CONFIG
# Sets the browser tab title/icon and overall layout. Must be the first
# Streamlit command that runs.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PathNav — Accommodation Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# SHARED SETUP
# init_session_state() must run before any tab renders, since every tab
# assumes its session_state keys already exist (see utils/session_state.py).
# ---------------------------------------------------------------------------
init_session_state()
inject_css()
api_client = APIClient()

# ---------------------------------------------------------------------------
# SIDEBAR — "About" section
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🧭 About PathNav")
    st.markdown(
        """
        **PathNav** helps college students turn their syllabi into an
        organized dashboard and understand their disability accommodation
        rights — all in one place.

        Use the tabs above to:
        - **Syllabus Scanner** — upload a syllabus PDF or enter a course by hand
        - **Table of Contents** — see all your courses, deadlines, and flagged accommodation language
        - **Policy Q&A** — ask questions about accommodation rights
        - **Navigator** — get step-by-step guidance for common situations
        - **Email Draft** — draft an accommodation email to a professor

        _This tool provides general information only and is not a
        substitute for advice from your university's disability services
        office or a legal professional._
        """
    )
    st.markdown("---")
    st.caption("Built for the Pathfinders Challenge 🌱")

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <h1>🧭 PathNav</h1>
        <p>Your AI-powered guide to organizing your courses and using your university disability accommodations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# TABS
# Each tab's content is a single render(...) call into components/ — keep
# it that way so two people can edit different tab files without merge
# conflicts in this one.
# ---------------------------------------------------------------------------
tab_scanner, tab_toc, tab_qa, tab_navigator, tab_email = st.tabs(
    ["📄 Syllabus Scanner", "📚 Table of Contents", "❓ Policy Q&A", "🧭 Navigator", "✉️ Email Draft"]
)

with tab_scanner:
    scanner_tab.render(api_client)

with tab_toc:
    toc_tab.render(api_client)

with tab_qa:
    policy_qa_tab.render(api_client)

with tab_navigator:
    navigator_tab.render()

with tab_email:
    email_draft_tab.render(api_client)
