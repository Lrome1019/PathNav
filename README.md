# PathNav

PathNav is a prototype web app for helping college students navigate syllabus accommodations, accommodation email drafting, and policy Q&A.

## What it does
- Scan syllabus PDFs and extract course details, deadlines, and accommodation language
- Let users enter courses manually if they don't have a PDF
- Draft accommodation emails based on selected courses and student context
- Answer policy questions about ADA / Section 504 accommodations
- Store course data in Streamlit session state for use across tabs

## Current status
- Frontend shell is built in Streamlit
- Backend integration is being implemented in `utils/api_client.py`
- The current branch `backend-api-integration` adds real PDF parsing with `pypdf` and Claude/Anthropic prompts for syllabus scan extraction, email generation, and policy Q&A

## Setup
1. Create a Python environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Anthropic API key:
   ```bash
   set ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Notes
- `utils/api_client.py` is the main integration point for backend calls
- `components/` contains the Streamlit tab pages
- `utils/session_state.py` defines the shared Streamlit state keys

## Branch / PR
- Active integration branch: `backend-api-integration`
- PR: https://github.com/Lrome1019/PathNav/pull/2

