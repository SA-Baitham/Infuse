import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.ui.styles import inject_css
from src.ui.pages import (
    render_dashboard,
    render_ingest,
    render_wiki,
    render_qa,
    render_health,
    render_output,
    render_settings,
)
from src.providers import ProviderRegistry
from src import config as cfg
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Infuse",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "active_provider" not in st.session_state:
    st.session_state.active_provider = None

with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">💉 <span>Infuse</span></div>',
        unsafe_allow_html=True,
    )

    pages = {
        "Dashboard": "📊",
        "Ingest": "📥",
        "Wiki": "📚",
        "Q&A": "❓",
        "Output": "🎨",
        "Health": "🏥",
        "Settings": "⚙️",
    }

    for page_name, icon in pages.items():
        active = "active" if st.session_state.page == page_name else ""
        if st.button(
            f"{icon} {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="secondary" if st.session_state.page != page_name else "primary",
        ):
            st.session_state.page = page_name
            st.rerun()

    st.divider()

    providers = cfg.get_connected_providers()
    if providers:
        provider_options = list(providers.keys())
        provider_labels = {}
        for pid in provider_options:
            pcls = ProviderRegistry.get(pid)
            name = pcls.meta.name if pcls else pid
            icon = pcls.meta.icon if pcls else "🔌"
            provider_labels[pid] = f"{icon} {name}"

        current = st.session_state.active_provider
        if current not in provider_options:
            current = provider_options[0]
            st.session_state.active_provider = current

        selected = st.selectbox(
            "Active Provider",
            options=provider_options,
            index=provider_options.index(current) if current in provider_options else 0,
            format_func=lambda x: provider_labels.get(x, x),
            key="sidebar_provider_select",
            label_visibility="collapsed",
        )
        if selected != st.session_state.active_provider:
            st.session_state.active_provider = selected
            st.rerun()

        pcls = ProviderRegistry.get(selected)
        pconfig = providers[selected]
        model = pconfig.get("model", "default")
        st.caption(f"Model: `{model}`")
    else:
        st.caption("No providers connected")

    st.divider()
    st.caption("Infuse v0.1")
    st.caption("Raw → Wiki → Q&A → Visualize")

page_routes = {
    "Dashboard": render_dashboard,
    "Ingest": render_ingest,
    "Wiki": render_wiki,
    "Q&A": render_qa,
    "Output": render_output,
    "Health": render_health,
    "Settings": render_settings,
}

render_fn = page_routes.get(st.session_state.page, render_dashboard)
render_fn()
