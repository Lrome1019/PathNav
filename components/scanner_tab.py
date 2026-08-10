"""
scanner_tab.py — "Syllabus Scanner" tab

Covers CRC classes FileUploadComponent + ManualInputForm (both owned by
Laura / Frontend 1). Lets a student either upload a syllabus PDF (scanned
automatically, per Epic A/B) or fill out a manual entry form as a fallback
(Epic A3/A4) when they don't have a scannable file. Either path adds a
course to the shared st.session_state.courses list that the Table of
Contents and Email Draft tabs read from.

Owner: Laura (Frontend 1)
"""

import streamlit as st

MAX_UPLOAD_MB = 20


def render(api_client) -> None:
    st.subheader("Scan a Syllabus")
    st.write(
        "Upload a syllabus PDF and we'll pull out the course info, deadlines, "
        "and any accommodation-related language automatically. No PDF? Enter "
        "the course by hand below instead."
    )

    # -----------------------------------------------------------------
    # PDF upload — client-side validation happens implicitly via the
    # `type=["pdf"]` filter; we still re-check size ourselves since
    # Streamlit's uploader doesn't enforce a max size on its own.
    # -----------------------------------------------------------------
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help=f"PDF files up to {MAX_UPLOAD_MB}MB.",
    )

    if uploaded_file is not None:
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_UPLOAD_MB:
            st.error(f"That file is {size_mb:.1f}MB — please upload something under {MAX_UPLOAD_MB}MB.")
        else:
            if st.button("Scan This Syllabus", key="scan_button"):
                with st.spinner("Scanning…"):
                    upload_result = api_client.upload_syllabus(uploaded_file.getvalue(), uploaded_file.name)
                    status_result = api_client.get_scan_status(upload_result["job_id"])

                if status_result["status"] == "complete":
                    st.session_state.courses.append(status_result["course"])
                    st.success(f"Scanned and added “{status_result['course']['name']}” to your Table of Contents.")
                elif status_result["status"] == "failed":
                    st.error("We couldn't read that file. Please try again or enter the course manually below.")
                else:
                    st.info("Still scanning — check back in a moment.")

    st.markdown("---")

    # -----------------------------------------------------------------
    # Manual entry fallback (Epic A3) — collapsed by default so the
    # upload path stays the primary call to action.
    # -----------------------------------------------------------------
    with st.expander("Don't have a PDF? Enter a course manually"):
        with st.form("manual_course_form"):
            col1, col2 = st.columns(2)
            with col1:
                course_name = st.text_input("Course name*", placeholder="e.g. Introduction to Psychology")
                course_code = st.text_input("Course code", placeholder="e.g. PSY 101")
            with col2:
                instructor = st.text_input("Instructor", placeholder="e.g. Dr. Amara Whitfield")
                term = st.text_input("Term", placeholder="e.g. Fall 2026")

            requirements_text = st.text_area(
                "Requirements / timeline",
                placeholder="e.g. Midterm on Oct 14, final project due Nov 20...",
                help="Free text for now — this becomes structured data once parsing is wired in.",
            )

            submitted = st.form_submit_button("Save Course")

        if submitted:
            if not course_name.strip():
                st.warning("Course name is required.")
            else:
                course = api_client.submit_manual_course(
                    {
                        "name": course_name.strip(),
                        "code": course_code.strip(),
                        "instructor": instructor.strip(),
                        "term": term.strip(),
                        "requirements": (
                            [{"date": "TBD", "type": "note", "description": requirements_text.strip(), "needs_review": False}]
                            if requirements_text.strip()
                            else []
                        ),
                    }
                )
                st.session_state.courses.append(course)
                st.success(f"Added “{course['name']}” to your Table of Contents.")

    # -----------------------------------------------------------------
    # Quick recap of what's been added this session.
    # -----------------------------------------------------------------
    if st.session_state.courses:
        st.markdown("#### Added this session")
        for course in st.session_state.courses:
            badge_class = "manual" if course["source"] == "manual" else ""
            st.markdown(
                f"- {course['name']} ({course.get('code', 'no code')}) "
                f"<span class='source-badge {badge_class}'>{course['source']}</span>",
                unsafe_allow_html=True,
            )
