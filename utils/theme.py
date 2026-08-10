"""
theme.py
--------
Shared color palette + CSS for the whole app. Everyone imports from here
instead of hard-coding hex values in their own tab file — if we ever want
to tweak the palette, this is the one place to change it.

Owner: Laura (Frontend 1) — shared utility, edit with a heads-up to the
team since it affects every tab's look.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# COLOR PALETTE — navy + teal, warm/accessible, WCAG-AA-friendly against
# white and cream backgrounds.
# ---------------------------------------------------------------------------
NAVY = "#13294B"
NAVY_LIGHT = "#1F3A63"
TEAL = "#2CA6A4"
TEAL_DARK = "#1E7F7D"
CREAM = "#F7F9FB"
TEXT_DARK = "#1A1A1A"
WARNING = "#B85C00"

# CSS class names available to every tab once inject_css() has run:
#   .response-box   -> teal-accented content card (Q&A answers, email preview)
#   .step-card      -> navy-accented card (Navigator steps, course detail)
#   .source-badge    -> small pill label (e.g. "Scanned" vs "Manual")
#   .review-flag     -> amber "needs review" badge


def inject_css() -> None:
    """Injects the app-wide stylesheet. Call once from app.py, before tabs render."""
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {CREAM};
            }}

            .app-header {{
                background: linear-gradient(90deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
                padding: 1.75rem 2rem;
                border-radius: 12px;
                margin-bottom: 1.5rem;
            }}
            .app-header h1 {{
                color: white;
                margin: 0;
                font-size: 2.1rem;
            }}
            .app-header p {{
                color: {CREAM};
                margin: 0.35rem 0 0 0;
                font-size: 1.05rem;
                opacity: 0.9;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 4px;
            }}
            .stTabs [data-baseweb="tab"] {{
                background-color: white;
                border-radius: 8px 8px 0 0;
                padding: 10px 18px;
                color: {NAVY};
                font-weight: 600;
            }}
            .stTabs [aria-selected="true"] {{
                background-color: {TEAL} !important;
                color: white !important;
            }}

            .stButton > button {{
                background-color: {TEAL};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 0.5rem 1.2rem;
            }}
            .stButton > button:hover {{
                background-color: {TEAL_DARK};
                color: white;
            }}

            .response-box {{
                background-color: white;
                border-left: 5px solid {TEAL};
                border-radius: 8px;
                padding: 1.2rem 1.4rem;
                color: {TEXT_DARK};
                min-height: 90px;
            }}

            .step-card {{
                background-color: white;
                border: 1px solid #E1E6EC;
                border-left: 5px solid {NAVY};
                border-radius: 8px;
                padding: 1.4rem;
                color: {TEXT_DARK};
            }}
            .step-card h4 {{
                color: {NAVY};
                margin-top: 0;
            }}

            .source-badge {{
                display: inline-block;
                background-color: {NAVY};
                color: white;
                font-size: 0.75rem;
                font-weight: 600;
                padding: 2px 10px;
                border-radius: 999px;
                margin-left: 8px;
            }}
            .source-badge.manual {{
                background-color: {TEAL_DARK};
            }}

            .review-flag {{
                display: inline-block;
                background-color: #FFF3E0;
                color: {WARNING};
                border: 1px solid {WARNING};
                font-size: 0.75rem;
                font-weight: 600;
                padding: 2px 10px;
                border-radius: 999px;
                margin-left: 8px;
            }}

            section[data-testid="stSidebar"] {{
                background-color: {NAVY};
            }}
            section[data-testid="stSidebar"] * {{
                color: {CREAM} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
