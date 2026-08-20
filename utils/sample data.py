"""
sample_data.py
---------------
Static placeholder content used before the real backend/API and Claude
integration exist. Nothing here is a real answer or real course data —
it just gives every tab something believable to render during frontend
development.

Owner: shared. Frontend Teammate mainly reads NAVIGATOR_GUIDES and
SAMPLE_COURSES; Laura mainly reads EXAMPLE_QUESTIONS.
"""

# ---------------------------------------------------------------------------
# Policy Q&A — example questions users can click to auto-fill the input.
# ---------------------------------------------------------------------------
EXAMPLE_QUESTIONS = [
    "What is the difference between accommodations under the ADA and Section 504?",
    "Can my professor refuse an accommodation approved by disability services?",
    "How long does it take to get an accommodation approved?",
    "Do I need to disclose my diagnosis to my professor?",
]

# ---------------------------------------------------------------------------
# Navigator — step-by-step guides per situation. A teammate may later
# generate these dynamically via the Claude API instead of a fixed dict.
# ---------------------------------------------------------------------------
NAVIGATOR_GUIDES = {
    "Request an accommodation": [
        "Contact your campus disability services (or 'accessibility services') office.",
        "Gather documentation of your diagnosis or condition from a healthcare provider.",
        "Complete the intake or registration form required by your office.",
        "Meet with a disability services coordinator to discuss eligible accommodations.",
        "Receive your official accommodation letter.",
        "Share the accommodation letter with each of your professors.",
    ],
    "Professor denied my accommodation": [
        "Stay calm — professors cannot unilaterally deny an approved accommodation.",
        "Document the denial: note the date, what was said, and get it in writing if possible.",
        "Re-share your official accommodation letter with the professor.",
        "Contact your disability services coordinator to report the issue.",
        "Request a joint meeting with you, the professor, and disability services.",
        "If unresolved, file a formal grievance through your university's process.",
    ],
    "I have a new diagnosis": [
        "Obtain official documentation from a licensed healthcare provider.",
        "Contact disability services to update or open your file.",
        "Discuss which accommodations may be appropriate for your new diagnosis.",
        "Complete any additional intake paperwork required.",
        "Receive your updated accommodation letter.",
        "Share the updated letter with your current professors.",
    ],
    "I need an extension": [
        "Check your syllabus for the professor's stated late-work policy.",
        "Review your accommodation letter for any deadline flexibility provisions.",
        "Email your professor as early as possible, referencing your accommodation.",
        "Propose a specific, reasonable new deadline.",
        "Follow up with disability services if the professor doesn't respond.",
        "Keep a written record of your request and the professor's response.",
    ],
}

# ---------------------------------------------------------------------------
# Table of Contents — a couple of demo courses so the tab isn't empty
# before real scanning/manual entry has happened. Shares the same shape
# as courses added at runtime (see utils/session_state.py).
# ---------------------------------------------------------------------------
SAMPLE_COURSES = [
    {
        "id": "sample-1",
        "name": "Introduction to Psychology",
        "code": "PSY 101",
        "instructor": "Dr. Amara Whitfield",
        "term": "Fall 2026",
        "source": "scanned",
        "requirements": [
            {"date": "2026-09-05", "type": "reading", "description": "Ch. 1–2 reading response", "needs_review": False},
            {"date": "2026-10-14", "type": "exam", "description": "Midterm exam", "needs_review": False},
            {"date": "2026-11-20", "type": "project", "description": "Group presentation", "needs_review": True},
        ],
        "accommodation_excerpt": (
            "Students who require accommodations should contact the Office of "
            "Disability Services and provide documentation within the first two "
            "weeks of the semester."
        ),
        "accommodation_status": "found",
    },
    {
        "id": "sample-2",
        "name": "Calculus II",
        "code": "MATH 202",
        "instructor": "Prof. David Chen",
        "term": "Fall 2026",
        "source": "manual",
        "requirements": [
            {"date": "2026-09-12", "type": "assignment", "description": "Problem set 1", "needs_review": False},
            {"date": "2026-10-03", "type": "exam", "description": "Exam 1", "needs_review": False},
        ],
        "accommodation_excerpt": None,
        "accommodation_status": "none_found",
    },
]
