# PathNav — Team Build Guide

How the three of us split this app and how to work on it together without
constantly merge-conflicting each other.

## Why it's split into files this way

Streamlit apps are easy to write as one giant `app.py`, but that's the
worst possible shape for a 3-person team — every person's changes land on
the same lines and every commit conflicts. Instead:

- **`app.py`** is just the shell: page config, theme, sidebar, and the
  five `st.tabs(...)` calls. It should almost never need edits once the
  tab list is settled.
- **`components/`** has one file per tab. You only ever edit *your* tab's
  file for day-to-day feature work.
- **`utils/`** has the stuff every tab shares: colors/CSS
  (`theme.py`), the placeholder backend wrapper (`api_client.py`), the
  list of shared `st.session_state` keys (`session_state.py`), and static
  placeholder content (`sample_data.py`). Changes here affect everyone,
  so give a heads-up in your team chat before editing.

## Who owns what

| Person | Files | Tabs |
|---|---|---|
| **Laura (Frontend 1)** | `app.py`, `components/scanner_tab.py`, `components/policy_qa_tab.py`, `components/email_draft_tab.py` | Syllabus Scanner, Policy Q&A, Email Draft |
| **Frontend Teammate** | `components/navigator_tab.py`, `components/toc_tab.py` | Navigator, Table of Contents |
| **Backend/API Teammate** | eventually a `backend/` or separate service; in the meantime, the *insides* of `utils/api_client.py`'s methods | n/a (all tabs call it) |

`utils/api_client.py` is the handoff point with the backend teammate:
every method already documents the request/response shape it should
eventually have (e.g. `upload_syllabus`, `get_policy_answer`,
`generate_email_draft`). Right now each method just returns canned data.
When real endpoints (or the Claude API) exist, only the *inside* of
these methods needs to change — no tab file should need to change,
because they only ever call `api_client.<method>(...)`.

## The shared session_state contract

Two people editing Streamlit tabs in parallel will eventually collide on
`st.session_state` keys unless there's one shared list. That list lives
in `utils/session_state.py` — every key the app uses is declared and
defaulted there, once, in `init_session_state()` (called at the top of
`app.py` before any tab renders).

The one key both of your tab sets touch is `st.session_state.courses` —
Laura's Scanner tab appends to it, and your Table of Contents / Email
Draft tabs read from it. If you need a new shared key, add it to
`init_session_state()` and mention it in your PR so the other person
knows it exists — don't invent a new key inline in a tab file.

## Git workflow

1. Branch per tab/feature: `git checkout -b navigator-tab` or similar.
2. Work only in your owned files (see table above) unless you're adding
   a genuinely shared utility — in that case, flag it to the team first.
3. Open a PR, tag the other frontend person for a quick look (mostly to
   check you didn't touch `utils/session_state.py` in a way that breaks
   their tab), merge to `main`.
4. Rebase/pull before starting new work so you're not building on a
   stale `utils/` contract.

## Running it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What's still placeholder

Every "AI" response (`get_policy_answer`, `generate_email_draft`) and
every "backend" call (`upload_syllabus`, `get_scan_status`,
`update_accommodation`) in `utils/api_client.py` returns fake data right
now. That's expected — frontend build-out doesn't need to wait on the
backend. The Table of Contents tab also ships with two sample courses
(`utils/sample_data.py`) so it isn't empty before real scanning exists.
