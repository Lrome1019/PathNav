"""
api_client.py
--------------
APIClient — the single wrapper every tab uses to "talk to the backend."

Right now every method returns placeholder data instead of making a real
HTTP request, because the Backend/API teammate hasn't stood up endpoints
yet. That's intentional: frontend work isn't blocked on backend work.

CONTRACT FOR THE BACKEND/API TEAMMATE:
  Each method below documents the request it should eventually make and
  the shape of data it must return. Keep method names and return shapes
  the same when you wire in the real API / Claude calls — every tab file
  calls these methods, not requests.post(...) directly, so swapping the
  internals here is the *only* change needed to go from placeholder to
  real backend. Please don't change a method's return shape without
  updating this docstring and pinging the frontend owners (Laura /
  Frontend Teammate) — both tabs read these shapes.

Owner: Laura (Frontend 1), shared utility — built collaboratively with
Backend/API Teammate since it mirrors their planned endpoints.
"""

import time
import uuid


class APIClient:
    """Thin wrapper around backend calls. Instantiate once in app.py and
    pass it into each tab's render() function.
    """

    # ------------------------------------------------------------------
    # Epic A/B — Syllabus upload, scanning & manual entry
    # ------------------------------------------------------------------
    def upload_syllabus(self, file_bytes: bytes, filename: str) -> dict:
        """POST /upload — send a PDF for scanning.

        Real version: multipart POST of the file, returns a job/file ID
        the frontend can poll via get_scan_status().

        Returns: {"job_id": str, "filename": str}
        """
        return {"job_id": f"job-{uuid.uuid4().hex[:8]}", "filename": filename}

    def get_scan_status(self, job_id: str) -> dict:
        """GET /scan-status/{job_id} — poll parsing status.

        Real version: returns one of queued/processing/complete/failed,
        plus the structured course JSON once complete.

        Returns: {"status": "complete", "course": {...}}  (placeholder
        always reports instant completion with a canned course record)
        """
        return {
            "status": "complete",
            "course": {
                "id": f"scan-{uuid.uuid4().hex[:8]}",
                "name": "New Scanned Course",
                "code": "TBD 000",
                "instructor": "TBD",
                "term": "TBD",
                "source": "scanned",
                "requirements": [
                    {"date": "TBD", "type": "assignment", "description": "Placeholder — parsing not yet connected", "needs_review": True},
                ],
                "accommodation_excerpt": None,
                "accommodation_status": "not_scanned",
            },
        }

    def submit_manual_course(self, course_data: dict) -> dict:
        """POST /courses (manual entry) — save a hand-entered course using
        the same CourseModel shape as scanned courses (source='manual').

        Returns: the saved course dict, including a generated "id".
        """
        course = dict(course_data)
        course.setdefault("id", f"manual-{uuid.uuid4().hex[:8]}")
        course["source"] = "manual"
        course.setdefault("requirements", [])
        course.setdefault("accommodation_excerpt", None)
        course.setdefault("accommodation_status", "not_scanned")
        return course

    # ------------------------------------------------------------------
    # Epic E — Table of Contents / course detail
    # ------------------------------------------------------------------
    def get_courses(self) -> list:
        """GET /courses — list all courses (scanned + manual).
        Placeholder: the frontend currently keeps this list in
        st.session_state.courses instead of calling this; the real
        version will replace that with a live fetch.
        """
        return []

    # ------------------------------------------------------------------
    # Epic C — Accommodation detection / review
    # ------------------------------------------------------------------
    def update_accommodation(self, course_id: str, excerpt: str | None, dismissed: bool = False) -> dict:
        """PATCH /courses/{course_id}/accommodation — confirm, edit, or
        dismiss a detected accommodation excerpt.

        Returns: {"course_id": str, "accommodation_excerpt": str | None,
                    "accommodation_status": str}
        """
        return {
            "course_id": course_id,
            "accommodation_excerpt": None if dismissed else excerpt,
            "accommodation_status": "none_found" if dismissed else "found",
        }

    # ------------------------------------------------------------------
    # Epic F — Email draft generation
    # ------------------------------------------------------------------
    def generate_email_draft(self, courses: list, extra_context: dict | None = None) -> str:
        """POST /email-draft — compile selected courses' requirements,
        deadlines, and accommodations (plus optional free-form context
        like accommodation type / specific request) into a formatted
        subject + body.

        `courses` is a list of course dicts (see utils/session_state.py
        for the shape). `extra_context` optionally carries manual-form
        fields when no course is selected yet (accommodation_type,
        professor_name, course_name, specific_request).

        Returns: formatted email text (subject line + body combined).
        """
        extra_context = extra_context or {}
        professor = extra_context.get("professor_name", "").strip() or "[Professor Name]"
        accommodation_type = extra_context.get("accommodation_type", "").strip() or "[accommodation type]"
        specific_request = extra_context.get("specific_request", "").strip() or "[specific request]"

        if courses:
            course_names = ", ".join(f"{c['name']} ({c.get('code', '')})".strip() for c in courses)
        else:
            course_names = extra_context.get("course_name", "").strip() or "[Course Name]"

        pending_note = ""
        if any(r.get("needs_review") for c in courses for r in c.get("requirements", [])):
            pending_note = (
                "\n\nNote: some included items are still marked pending "
                "confirmation and should be double-checked against the "
                "original syllabus."
            )

        return (
            f"Subject: Accommodation Request for {course_names}\n\n"
            f"Dear Professor {professor},\n\n"
            f"I hope this email finds you well. I am reaching out to request "
            f"{accommodation_type} for {course_names}, specifically regarding "
            f"{specific_request}.\n\n"
            f"[Placeholder — personalized explanation generated by AI will "
            f"appear here once the Claude API is connected.]"
            f"{pending_note}\n\n"
            f"Please let me know if you need any additional documentation from "
            f"Disability Services. I appreciate your support and am happy to "
            f"discuss further at your convenience.\n\n"
            f"Best regards,\n"
            f"[Your Name]"
        )

    # ------------------------------------------------------------------
    # Policy Q&A (new for PathNav — not in the original CRC cards, but
    # follows the same "backend owns the real call" pattern)
    # ------------------------------------------------------------------
    def get_policy_answer(self, question: str) -> str:
        """POST /policy-qa — ask a general accommodation-rights question.

        Real version: sends `question` to the Claude API (optionally with
        retrieved policy documents) and returns a generated answer.

        Returns: answer text.
        """
        return (
            "**[Placeholder response]**\n\n"
            f"You asked: _\"{question}\"_\n\n"
            "This is where an AI-generated answer about accommodation rights, "
            "ADA/Section 504 policy, or university-specific procedures will "
            "appear once the Claude API is connected."
        )
