import io
import json
import os
import re
import uuid
from typing import Any

from anthropic import Anthropic
from pypdf import PdfReader

POLICY_SECTIONS = {
    "ADA": (
        "The Americans with Disabilities Act (ADA) requires colleges and universities "
        "to provide reasonable accommodations so students with disabilities have equal "
        "access to academic programs."
    ),
    "Section 504": (
        "Section 504 of the Rehabilitation Act prohibits disability discrimination in "
        "federally funded programs, including most U.S. colleges and universities."
    ),
    "Campus guidance": (
        "PathNav helps students understand disability accommodations under the ADA "
        "and Section 504. Provide clear, campus-relevant guidance where possible. "
        "If specific university policy is not available, answer based on general "
        "U.S. ADA and Section 504 disability accommodation principles, and encourage "
        "the student to consult their campus disability services office."
    ),
    "Legal disclaimer": (
        "Do not offer legal advice. This is general information, not a determination "
        "of rights in a specific case."
    ),
}

POLICY_CONTEXT = "\n\n".join(
    f"{name}: {text}" for name, text in POLICY_SECTIONS.items()
)

COURSE_EXTRACTION_INSTRUCTIONS = (
    "Extract course metadata from the syllabus text and return a single JSON object "
    "with the following exact keys: id, name, code, instructor, term, source, "
    "requirements, accommodation_excerpt, accommodation_status. "
    "Use 'scanned' for source. "
    "requirements must be a list of objects with keys: date, type, description, needs_review. "
    "If the syllabus includes accommodation language, set accommodation_excerpt to the exact extracted passage and accommodation_status to 'found'. "
    "If no accommodation language is present, set accommodation_excerpt to null and accommodation_status to 'none_found'. "
    "If you cannot extract a field, use empty string for text fields and an empty list for requirements. "
    "Return only valid JSON, with no additional explanatory text."
)


class APIClient:
    """Thin wrapper around backend calls. Instantiate once in app.py and
    pass it into each tab's render() function. The internals call Anthropic
    and/or local PDF parsing while preserving the frontend contract.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or self._resolve_api_key()
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self._scan_jobs: dict[str, dict[str, str]] = {}
        self._courses: list[dict[str, Any]] = []

    @staticmethod
    def _resolve_api_key() -> str | None:
        try:
            import streamlit as st

            secret = st.secrets["ANTHROPIC_API_KEY"]
            if secret:
                return str(secret)
        except Exception:
            pass
        return os.getenv("ANTHROPIC_API_KEY")

    @staticmethod
    def _show_friendly_error(message: str) -> None:
        try:
            import streamlit as st

            st.error(message)
        except Exception:
            pass

    def _ensure_client(self) -> Anthropic:
        if not self.client:
            raise RuntimeError(
                "Anthropic API client is not configured. Set ANTHROPIC_API_KEY."
            )
        return self.client

    def _call_claude(
        self,
        prompt: str,
        max_tokens: int = 1200,
        system: str = "You are a helpful assistant for PathNav.",
    ) -> str:
        try:
            client = self._ensure_client()
            resp = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            for block in resp.content:
                if getattr(block, "type", None) == "text":
                    return block.text
            return ""
        except RuntimeError:
            self._show_friendly_error(
                "PathNav couldn't reach Claude because no API key is configured. "
                "Add ANTHROPIC_API_KEY in Streamlit secrets or your environment, then try again."
            )
            return ""
        except Exception:
            self._show_friendly_error(
                "PathNav couldn't reach Claude right now. Please try again in a moment."
            )
            return ""

    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()
        except Exception:
            return ""

    def _parse_json_response(self, response_text: str) -> dict[str, Any]:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in Claude response.")
        payload = match.group(0)
        return json.loads(payload)

    def _extract_course_from_syllabus(
        self, text: str, filename: str
    ) -> dict[str, Any] | None:
        prompt = (
            f"You are an assistant that extracts course information from syllabus text. "
            f"The syllabus filename is {filename}. "
            f"Here is the raw syllabus text:\n\n{text}\n\n"
            f"{COURSE_EXTRACTION_INSTRUCTIONS}"
        )
        response = self._call_claude(prompt, max_tokens=1000)
        if not response:
            return None
        try:
            course = self._parse_json_response(response)
        except Exception:
            course = {
                "id": f"scan-{uuid.uuid4().hex[:8]}",
                "name": "Scanned Course",
                "code": "",
                "instructor": "",
                "term": "",
                "source": "scanned",
                "requirements": [],
                "accommodation_excerpt": None,
                "accommodation_status": "none_found",
            }
        return course

    def upload_syllabus(self, file_bytes: bytes, filename: str) -> dict:
        """Uploads a syllabus PDF and returns a polling job ID."""
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        self._scan_jobs[job_id] = {
            "filename": filename,
            "text": self._extract_text_from_pdf(file_bytes),
        }
        return {"job_id": job_id, "filename": filename}

    def get_scan_status(self, job_id: str) -> dict:
        """Returns scan status and the structured course JSON when complete."""
        job = self._scan_jobs.get(job_id)
        if not job:
            return {"status": "failed", "error": "unknown job_id"}

        if not job["text"]:
            return {"status": "failed", "error": "unable to parse PDF text"}

        course = self._extract_course_from_syllabus(job["text"], job["filename"])
        if not course:
            return {"status": "failed", "error": "llm_error"}
        return {"status": "complete", "course": course}

    def submit_manual_course(self, course_data: dict) -> dict:
        """Saves a hand-entered course and returns the created course object."""
        course = dict(course_data)
        course.setdefault("id", f"manual-{uuid.uuid4().hex[:8]}")
        course.setdefault("source", "manual")
        course.setdefault("requirements", [])
        course.setdefault("accommodation_excerpt", None)
        course.setdefault("accommodation_status", "not_scanned")
        self._courses.append(course)
        return course

    def get_courses(self) -> list[dict[str, Any]]:
        """Returns courses created or stored by this client."""
        return list(self._courses)

    def update_accommodation(
        self, course_id: str, excerpt: str | None, dismissed: bool = False
    ) -> dict:
        """Updates accommodation excerpt state for a course."""
        return {
            "course_id": course_id,
            "accommodation_excerpt": None if dismissed else excerpt,
            "dismissed": dismissed,
        }

    def generate_email_draft(
        self, courses: list[dict[str, Any]], extra_context: dict | None = None
    ) -> str:
        """Generates a tailored accommodation email draft."""
        extra_context = extra_context or {}
        course_descriptions = []
        for course in courses:
            course_descriptions.append(
                f"{course.get('name', '')} ({course.get('code', '')}) taught by "
                f"{course.get('instructor', 'TBD')} in {course.get('term', 'TBD')} "
                f"with requirements {course.get('requirements', [])}."
            )

        prompt = (
            "You are an expert assistant writing a professional accommodation email. "
            "Write a concise but respectful email with a subject line and body. "
            "Use the provided course information and student context. "
            "Return only the email text, beginning with 'Subject:'.\n\n"
            f"Selected courses:\n{chr(10).join(course_descriptions) if course_descriptions else 'None'}\n\n"
            f"Student context:\nAccommodation type: {extra_context.get('accommodation_type', '')}\n"
            f"Professor name: {extra_context.get('professor_name', '')}\n"
            f"Course name: {extra_context.get('course_name', '')}\n"
            f"Specific request: {extra_context.get('specific_request', '')}\n"
        )
        return self._call_claude(prompt, max_tokens=800)

    def get_policy_answer(self, question: str) -> dict[str, str] | None:
        """Returns a Claude-generated policy answer and the POLICY_CONTEXT section used."""
        section_names = ", ".join(POLICY_SECTIONS)
        prompt = (
            f"Question: {question}\n\n"
            "Provide a plain-language answer and avoid giving legal advice. "
            "Name the single POLICY_CONTEXT section you drew from most. "
            "Return only valid JSON with keys answer and source_section. "
            f"source_section must be one of: {section_names}."
        )
        response = self._call_claude(
            prompt,
            max_tokens=600,
            system=(
                "You are an expert on U.S. disability accommodation policy, including "
                "ADA and Section 504. Use only the following policy context and cite "
                "the section you used.\n\n"
                f"{POLICY_CONTEXT}"
            ),
        )
        if not response:
            return None
        try:
            payload = self._parse_json_response(response)
            answer = str(payload.get("answer", "")).strip()
            source = str(payload.get("source_section", "")).strip()
            if source not in POLICY_SECTIONS:
                source = next(
                    (
                        name
                        for name in POLICY_SECTIONS
                        if name.lower() == source.lower()
                    ),
                    source or "Campus guidance",
                )
            return {
                "answer": answer or response,
                "source_section": source,
            }
        except Exception:
            return {
                "answer": response,
                "source_section": "Campus guidance",
            }
