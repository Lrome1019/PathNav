"""
session_state.py
-----------------
Single source of truth for every st.session_state key the app uses.

Why this file exists: with two people editing Streamlit tabs in parallel,
the #1 way to break each other's code is one person renaming/repurposing a
session_state key another tab already depends on. Instead of each tab file
inventing its own keys ad hoc, every key is declared and defaulted here,
once, at startup. If you need a new piece of shared state, add it to
init_session_state() and mention it in the PATHNAV_TEAM_GUIDE.md table so
your teammate knows it exists.

Owner: Laura (Frontend 1) — shared utility.
"""

import streamlit as st


def init_session_state() -> None:
    """Sets default values for all session_state keys. Call once from app.py,
    before any tab renders, so every tab can safely assume these keys exist.
    """

    defaults = {
        # --- Syllabus Scanner tab (Laura) ---------------------------------
        # "courses" is the shared course list every tab reads from — the
        # closest thing this prototype has to the CourseModel table the
        # backend will eventually own. Each course dict shape:
        #   {
        #     "id": str,
        #     "name": str, "code": str, "instructor": str, "term": str,
        #     "source": "scanned" | "manual",
        #     "requirements": [{"date": str, "type": str, "description": str,
        #                        "needs_review": bool}, ...],
        #     "accommodation_excerpt": str | None,
        #     "accommodation_status": "not_scanned" | "none_found" | "found",
        #   }
        "courses": [],
        "scan_job_status": None,       # "queued" | "processing" | "complete" | "failed" | None
        "scan_uploaded_filename": None,

        # --- Policy Q&A tab (Laura) ----------------------------------------
        "policy_question": "",
        "policy_answer": None,

        # --- Email Draft tab (Laura) ---------------------------------------
        "generated_email": None,

        # --- Navigator tab (Frontend Teammate) ------------------------------
        "nav_situation": None,
        "nav_step_index": 0,

        # --- Table of Contents tab (Frontend Teammate) -----------------------
        "selected_course_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
