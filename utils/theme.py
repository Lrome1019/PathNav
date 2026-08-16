import streamlit as st

NAVY = "#001f3f"
TEAL = "#004d40"
TEAL_DARK = "#00332b"
CREAM = "#f5f5f5"

def inject_css() -> None:
    st.markdown(f"""
        <style>
            .stApp {{
                background-color: {CREAM};
            }}
             .app-header {{
             background-color: {NAVY};
             padding: 1rem; 2rem;
             border radius: 0 0 10px 10px;
             margin-bottom: 1.5rem;
        }}
        .app-header p {{
        color: {CREAM};
        margin-top: 0.5rem;
        opacity: 0.8;
        }} 
        </style>
    """, unsafe_allow_html=True)
