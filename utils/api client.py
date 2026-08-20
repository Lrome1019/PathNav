import io
import json
import os
import re
import uuid
from typing import Any

from anthropic import AI_PROMPT, Anthropic, HUMAN_PROMPT
from pypdf import PdfReader

POLICY_CONTEXT = (
    "PathNav helps students understand disability accommodations under the ADA "
    "and Section 504. Provide clear, campus-relevant guidance where possible, "
    "but do not offer legal advice. If specific university policy is not "
    "available, answer based on general U.S. ADA and Section 504 disability "
    "accommodation principles."
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
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3.5")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self._scan_jobs: dict[str, dict[str, str]] = {}
        self._courses: list[dict[str, Any]] = []

    def _ensure_client(self) -> Anthropic:
        if not self.client:
            raise RuntimeError(
                "Anthropic API client is not configured. Set ANTHROPIC_API_KEY."
            )
        return self.client

    def _call_claude(self, prompt: str, max_tokens: int = 1200) -> str:
        client = self._ensure_client()
        completion = client.completions.create(
            model=self.model,
            prompt=f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}",
            max_tokens_to_sample=max_tokens,
        )
        return getattr(completion, "completion", completion.get("completion", ""))

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

    def _extract_course_from_syllabus(self, text: str, filename: str) -> dict[str, Any]:
        prompt = (
            f"You are an assistant that extracts course information from syllabus text. "
            f"The syllabus filename is {filename}. "
            f"Here is the raw syllabus text:\n\n{text}\n\n"
            f"{COURSE_EXTRACTION_INSTRUCTIONS}"
        )
        response = self._call_claude(prompt, max_tokens=1000)
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

    def get_policy_answer(self, question: str) -> str:
        """Returns a Claude-generated policy answer for the given question."""
        prompt = (
            f"You are an expert on U.S. disability accommodation policy, including ADA "
            f"and Section 504. Answer the student's question clearly and helpfully. "
            f"Base your response on general policy guidance and encourage the user to "
            f"consult their campus disability services office for school-specific details.\n\n"
            f"Policy context:\n{POLICY_CONTEXT}\n\n"
            f"Question: {question}\n\n"
            "Provide a plain-language answer and avoid giving legal advice."
        )
        return self._call_claude(prompt, max_tokens=600)
