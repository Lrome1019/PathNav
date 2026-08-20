"""
toc_tab.py — "Table of Contents" tab

Covers CRC classes TableOfContentsTab, CourseDetailView, and
AccommodationEditor (Epics E and C). Lists every course (scanned or
manual), lets the student click into one to see its requirements sorted
chronologically with "needs review" flags, and lets them confirm, edit,
or dismiss the detected accommodation excerpt.

Owner: Frontend Teammate
(scaffolded by Laura so the team has a working starting point — please
make this your own! natural next steps: swap SAMPLE_COURSES for a real
GET /courses call once the backend exists, add search/filter (E5), style
the course list as cards instead of a selectbox.)
"""

import streamlit as st

from utils.loader import load

SAMPLE_COURSES = load("utils/sample data.py").SAMPLE_COURSES


def render(api_client) -> None:
    st.subheader("Your Courses")

    # Demo courses ship with the app so this tab isn't empty on first
    # run; anything added via the Scanner tab this session is appended
    # after them. Once the backend exists, replace this concatenation
    # with `courses = api_client.get_courses()`.
    courses = SAMPLE_COURSES + st.session_state.courses

    if not courses:
        st.info("No courses yet. Add one from the **Syllabus Scanner** tab to get started.")
        return

    # -----------------------------------------------------------------
    # Course list (E1) — name/code + source badge, click to view detail.
    # -----------------------------------------------------------------
    labels = [f"{c['name']} ({c.get('code', 'no code')})" for c in courses]
    default_index = 0
    if st.session_state.selected_course_id:
        matching = [i for i, c in enumerate(courses) if c["id"] == st.session_state.selected_course_id]
        if matching:
            default_index = matching[0]

    chosen_label = st.selectbox("Select a course", options=labels, index=default_index, key="toc_course_select")
    course = courses[labels.index(chosen_label)]
    st.session_state.selected_course_id = course["id"]

    badge_class = "manual" if course["source"] == "manual" else ""
    st.markdown(
        f"### {course['name']} <span class='source-badge {badge_class}'>{course['source']}</span>",
        unsafe_allow_html=True,
    )
    st.caption(f"{course.get('code', '')} · {course.get('instructor', 'Instructor TBD')} · {course.get('term', '')}")

    # -----------------------------------------------------------------
    # Requirements & timeline (E2) — sorted chronologically, flagged
    # items visually marked.
    # -----------------------------------------------------------------
    st.markdown("#### Requirements & Timeline")
    requirements = sorted(course.get("requirements", []), key=lambda r: r.get("date", ""))

    if not requirements:
        st.write("No requirements extracted yet.")
    else:
        for req in requirements:
            flag_html = "<span class='review-flag'>needs review</span>" if req.get("needs_review") else ""
            st.markdown(
                f"- **{req.get('date', 'TBD')}** — _{req.get('type', 'item')}_: "
                f"{req.get('description', '')} {flag_html}",
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------------------
    # Accommodation review (C3/E4) — confirm, edit, or dismiss.
    # -----------------------------------------------------------------
    st.markdown("#### Accommodation Language")
    status = course.get("accommodation_status", "not_scanned")

    if status == "not_scanned":
        st.write("This course hasn't been scanned for accommodation language yet.")
    elif status == "none_found":
        st.write("No accommodation statement was found in this syllabus.")
    else:
        excerpt = course.get("accommodation_excerpt") or ""
        edited = st.text_area("Detected excerpt", value=excerpt, key=f"accommodation_text_{course['id']}")

        confirm_col, dismiss_col = st.columns(2)
        with confirm_col:
            if st.button("✅ Confirm / Save Edit", key=f"confirm_accommodation_{course['id']}", use_container_width=True):
                api_client.update_accommodation(course["id"], edited, dismissed=False)
                course["accommodation_excerpt"] = edited
                course["accommodation_status"] = "found"
                st.success("Saved.")
        with dismiss_col:
            if st.button("✖ Dismiss", key=f"dismiss_accommodation_{course['id']}", use_container_width=True):
                api_client.update_accommodation(course["id"], None, dismissed=True)
                course["accommodation_excerpt"] = None
                course["accommodation_status"] = "dismissed"
                st.info("Dismissed — marked as reviewed.")
