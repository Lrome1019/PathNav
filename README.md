# PathNav

PathNav is a prototype Streamlit app that helps college students navigate syllabus accommodations, draft accommodation emails, and ask policy questions about ADA / Section 504.

## What it does
- Scan syllabus PDFs and extract course details, deadlines, and accommodation language
- Let users enter courses manually if they don't have a PDF
- Review courses, requirements, and detected accommodation language
- Draft accommodation emails based on selected courses and student context
- Answer policy questions about ADA / Section 504 accommodations
- Walk through common accommodation situations step by step
- Store course data in Streamlit session state for use across tabs

## Setup (Mac)

1. From the PathNav folder, create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your Anthropic API key. Copy the example secrets file and paste your key:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   Then edit `.streamlit/secrets.toml`. You can also export it in your shell instead:

   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

   Do not commit `.streamlit/secrets.toml` or `.env`.

4. Run the app:

   ```bash
   streamlit run app.py
   ```

   Then open http://localhost:8501

On Streamlit Community Cloud, set `ANTHROPIC_API_KEY` in the app's Secrets settings instead of committing a secrets file.

## Notes
- `app.py` mounts five tabs: Syllabus Scanner, Table of Contents, Email Draft, Policy Q&A, and Navigator
- `utils/api_client.py` is the backend wrapper (PDF parsing + Claude Messages API, model `claude-sonnet-5`)
- `components/` contains the Streamlit tab pages
- `utils/session_state.py` defines the shared Streamlit state keys
- Navigator and Table of Contents work without an API key; Scanner, Email Draft, and Policy Q&A need one
