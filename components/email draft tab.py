"""
email_draft_tab.py — "Email Draft" tab

Covers CRC class EmailDraftTab (Epic F). If courses already exist (from
the Scanner tab), the student checks off which ones to include, per F2.
Otherwise — or in addition — they can fill in the accommodation details
by hand. Either path calls APIClient.generate_email_draft() to produce a
preview, then offers copy-to-clipboard and a mailto: link (F4).

Owner: Laura (Frontend 1)
"""

import json

import streamlit as st
import streamlit.components.v1 as components

from utils.theme import TEAL, TEAL_DARK


def render(api_client) -> None:
    st.subheader("Draft an Accommodation Email")

    courses = st.session_state.courses
    selected_courses = []

    if courses:
        st.write("Select which courses to include, then fill in a bit more context.")
        st.markdown("**Include courses:**")
        for course in courses:
            checked = st.checkbox(
                f"{course['name']} ({course.get('code', 'no code')})",
                value=True,
                key=f"email_include_{course['id']}",
            )
            if checked:
                selected_courses.append(course)
    else:
        st.write(
            "You haven't added any courses yet. Fill in the details below and "
            "generate a professional email to send to your professor or "
            "disability services office — or add a course on the Syllabus "
            "Scanner tab first to pull requirements in automatically."
        )

    with st.form("email_drafter_form"):
        col1, col2 = st.columns(2)
        with col1:
            accommodation_type = st.text_input(
                "Accommodation type",
                placeholder="e.g. Extended test time, note-taker, flexible deadlines",
            )
            professor_name = st.text_input("Professor name", placeholder="e.g. Dr. Smith")
        with col2:
            course_name = st.text_input(
                "Course name",
                placeholder="e.g. Introduction to Psychology (PSY 101)",
                disabled=bool(selected_courses),
                help="Disabled because you've selected course(s) above." if selected_courses else None,
            )
            specific_request = st.text_input(
                "Specific request",
                placeholder="e.g. 1.5x time on exams, permission to record lectures",
            )

        generate_clicked = st.form_submit_button("Generate Email")

    st.markdown("#### Email Preview")

    if generate_clicked:
        if not accommodation_type.strip() or not specific_request.strip():
            st.warning("Please fill in at least the accommodation type and specific request.")
        else:
            st.session_state.generated_email = api_client.generate_email_draft(
                selected_courses,
                extra_context={
                    "accommodation_type": accommodation_type,
                    "professor_name": professor_name,
                    "course_name": course_name,
                    "specific_request": specific_request,
                },
            )

    email_text = st.session_state.generated_email or (
        "Your drafted email will appear here once you click \"Generate Email.\""
    )

    st.markdown(
        f'<div class="response-box"><pre style="white-space: pre-wrap; '
        f'font-family: inherit; margin:0;">{email_text}</pre></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.generated_email:
        _render_copy_and_mailto(st.session_state.generated_email)


def _render_copy_and_mailto(email_text: str) -> None:
    """Copy-to-clipboard button + mailto: link (F4). Implemented with a
    small embedded JS snippet since Streamlit has no native clipboard
    widget or way to open mailto: links from a plain st.button.
    """
    # Split "Subject: ...\n\n<body>" back into parts for the mailto link.
    if email_text.startswith("Subject:"):
        first_line, _, body = email_text.partition("\n\n")
        subject = first_line.replace("Subject:", "", 1).strip()
    else:
        subject, body = "Accommodation Request", email_text

    copy_payload = json.dumps(email_text)
    mailto_subject = json.dumps(subject)
    mailto_body = json.dumps(body)

    components.html(
        f"""
        <button id="copy-email-btn" style="
            background-color: {TEAL}; color: white; border: none; border-radius: 8px;
            font-weight: 600; padding: 0.5rem 1.2rem; cursor: pointer; margin-top: 0.5rem;
        ">📋 Copy to Clipboard</button>
        <button id="mailto-btn" style="
            background-color: {TEAL_DARK}; color: white; border: none; border-radius: 8px;
            font-weight: 600; padding: 0.5rem 1.2rem; cursor: pointer; margin-top: 0.5rem; margin-left: 8px;
        ">✉️ Open in Email</button>
        <span id="copy-status" style="margin-left: 10px; font-family: sans-serif; color: {TEAL_DARK};"></span>
        <script>
            document.getElementById("copy-email-btn").addEventListener("click", () => {{
                navigator.clipboard.writeText({copy_payload}).then(() => {{
                    document.getElementById("copy-status").innerText = "Copied!";
                }});
            }});
            document.getElementById("mailto-btn").addEventListener("click", () => {{
                const subject = encodeURIComponent({mailto_subject});
                const body = encodeURIComponent({mailto_body});
                window.open(`mailto:?subject=${{subject}}&body=${{body}}`, "_blank");
            }});
        </script>
        """,
        height=60,
    )
