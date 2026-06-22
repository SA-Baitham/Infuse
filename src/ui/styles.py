import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background: #0f0f11;
    }
    .main > div {
        padding: 1rem 2rem;
    }

    section[data-testid="stSidebar"] {
        background: #141417;
        border-right: 1px solid #27272a;
    }
    section[data-testid="stSidebar"] .st-emotion-cache-1cypcdb {
        padding: 2rem 1rem;
    }
    .sidebar-logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e4e4e7;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sidebar-logo span {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .provider-icon {
        font-size: 1.5rem;
        width: 2.5rem;
        height: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #27272a;
        border-radius: 10px;
        flex-shrink: 0;
    }
    .provider-info {
        flex: 1;
        min-width: 0;
    }
    .provider-name {
        font-weight: 600;
        color: #e4e4e7;
        font-size: 1rem;
    }
    .provider-desc {
        color: #71717a;
        font-size: 0.8rem;
        margin-top: 0.15rem;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #27272a;
    }

    .stat-card {
        background: #1a1a1e;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e4e4e7;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #71717a;
        margin-top: 0.25rem;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        border: none;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5558e6, #9a45f0);
    }

    h1, h2, h3 {
        color: #e4e4e7 !important;
    }
    h1 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
    }

    hr {
        border-color: #27272a !important;
    }

    .stTextInput > div > div > input {
        background: #1a1a1e !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        color: #e4e4e7 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }

    .streamlit-expanderHeader {
        background: #1a1a1e !important;
        border-radius: 8px !important;
        border: 1px solid #27272a !important;
    }
    .streamlit-expanderContent {
        background: #141417 !important;
        border: 1px solid #27272a !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    .stSelectbox > div > div {
        background: #1a1a1e !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }

    .stAlert {
        background: #1a1a1e !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }

    pre {
        background: #141417 !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
    code {
        color: #a78bfa !important;
    }

    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }
    .chat-message.assistant {
        background: #1e1e24;
        border: 1px solid #6366f1;
        border-left: 3px solid #6366f1;
    }
    </style>
    """, unsafe_allow_html=True)
