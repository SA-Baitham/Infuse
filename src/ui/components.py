import streamlit as st
import os
import httpx
from src.providers import ProviderRegistry, ConfigField
from src import config as cfg


def _env_val(field: ConfigField) -> str:
    if field.env_var:
        return os.environ.get(field.env_var, "")
    return ""


def render_provider_selection():
    popular = ProviderRegistry.popular()
    other = ProviderRegistry.other()
    all_providers = popular + other
    connected = cfg.get_connected_providers()

    search = st.text_input("🔍", placeholder="Search providers...", label_visibility="collapsed").lower()

    if search:
        all_providers = [p for p in all_providers if search in p.meta.name.lower() or search in p.meta.id.lower()]

    popular = [p for p in all_providers if p.meta.group == "Popular"]
    other = [p for p in all_providers if p.meta.group == "Other"]

    selected = None

    if popular:
        st.markdown('<div class="section-header">Popular</div>', unsafe_allow_html=True)
        for provider_cls in popular:
            pid = provider_cls.meta.id
            is_connected = pid in connected
            cols = st.columns([1, 4, 1])
            with cols[0]:
                st.markdown(f'<div class="provider-icon">{provider_cls.meta.icon}</div>',
                          unsafe_allow_html=True)
            with cols[1]:
                tag_html = ""
                if provider_cls.meta.tag:
                    tag_cls = "recommended" if provider_cls.meta.tag == "Recommended" else ""
                    tag_html = f'<span style="background:linear-gradient(135deg,#6366f1,#a855f7);color:white;font-size:0.65rem;padding:0.15rem 0.5rem;border-radius:999px;font-weight:600;margin-left:0.5rem">{provider_cls.meta.tag}</span>'
                st.markdown(
                    f'<div class="provider-info">'
                    f'<div class="provider-name">{provider_cls.meta.name}{tag_html}</div>'
                    f'<div class="provider-desc">{provider_cls.meta.description}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with cols[2]:
                if st.button("Connected" if is_connected else "Connect",
                            key=f"select_{pid}",
                            use_container_width=True,
                            disabled=is_connected):
                    selected = pid

    if other:
        st.markdown('<div class="section-header">Other</div>', unsafe_allow_html=True)
        for provider_cls in other:
            pid = provider_cls.meta.id
            is_connected = pid in connected
            cols = st.columns([1, 4, 1])
            with cols[0]:
                st.markdown(f'<div class="provider-icon">{provider_cls.meta.icon}</div>',
                          unsafe_allow_html=True)
            with cols[1]:
                st.markdown(
                    f'<div class="provider-info">'
                    f'<div class="provider-name">{provider_cls.meta.name}</div>'
                    f'<div class="provider-desc">{provider_cls.meta.description}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with cols[2]:
                if st.button("Connected" if is_connected else "Connect",
                            key=f"select_{pid}",
                            use_container_width=True,
                            disabled=is_connected):
                    selected = pid

    st.markdown('<div class="section-header">Custom</div>', unsafe_allow_html=True)
    cols = st.columns([1, 4, 1])
    with cols[0]:
        st.markdown('<div class="provider-icon">🔌</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(
            '<div class="provider-info">'
            '<div class="provider-name">Custom Provider</div>'
            '<div class="provider-desc">OpenAI-compatible endpoint with custom headers</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with cols[2]:
        if st.button("Add Custom", key="select_custom", use_container_width=True):
            selected = "__custom__"

    return selected


def render_connection_dialog(provider_id: str):
    connected = cfg.get_connected_providers()

    if provider_id == "__custom__":
        return _render_custom_provider_form()

    provider_cls = ProviderRegistry.get(provider_id)
    if not provider_cls:
        st.error(f"Unknown provider: {provider_id}")
        return None

    is_connected = provider_id in connected

    st.markdown(f"### Connect to {provider_cls.meta.name}")
    st.markdown(f"{provider_cls.meta.icon} {provider_cls.meta.description}")

    if is_connected:
        st.success(f"✅ {provider_cls.meta.name} is connected")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Disconnect", type="secondary", use_container_width=True):
                cfg.disconnect_provider(provider_id)
                st.rerun()
        with col2:
            if st.button("Reconfigure", use_container_width=True):
                cfg.disconnect_provider(provider_id)
                st.rerun()
        return provider_id

    config_values = {}
    for field in provider_cls.config_fields():
        default_val = _env_val(field)
        if field.type == "password":
            config_values[field.key] = st.text_input(
                field.label,
                type="password",
                placeholder=field.placeholder,
                value=default_val,
                key=f"cfg_{provider_id}_{field.key}",
            )
        elif field.type == "select" and field.options:
            config_values[field.key] = st.selectbox(
                field.label,
                field.options,
                key=f"cfg_{provider_id}_{field.key}",
            )
        else:
            config_values[field.key] = st.text_input(
                field.label,
                placeholder=field.placeholder,
                value=default_val,
                key=f"cfg_{provider_id}_{field.key}",
            )

    # Dynamic model fetching for Ollama
    ollama_models = None
    if provider_id == "ollama":
        base_url = config_values.get("base_url", "").rstrip("/") or "http://localhost:11434"
        if st.button("🔍 Fetch Models from Server", key=f"fetch_models_{provider_id}", use_container_width=True):
            with st.spinner("Fetching models..."):
                try:
                    r = httpx.get(f"{base_url}/api/tags", timeout=5)
                    r.raise_for_status()
                    ollama_models = [m["name"] for m in r.json().get("models", [])]
                    if not ollama_models:
                        st.warning("No models found on the server.")
                except Exception as e:
                    st.error(f"Failed to connect: {e}")
        if ollama_models:
            st.success(f"Found {len(ollama_models)} models")
            st.session_state[f"ollama_models_{provider_id}"] = ollama_models

    models = provider_cls.models
    if provider_id == "ollama":
        cached = st.session_state.get(f"ollama_models_{provider_id}")
        if cached:
            models = cached
    if not models:
        models = ["llama3", "mistral", "qwen2.5", "codellama"]
    selected_model = st.selectbox(
        "Default model",
        models,
        key=f"model_{provider_id}",
    )

    if st.button("Connect Provider", type="primary", use_container_width=True):
        missing = [f.key for f in provider_cls.config_fields()
                  if f.required and not config_values.get(f.key)]
        if missing:
            st.error(f"Please fill in: {', '.join(missing)}")
        else:
            config_values["model"] = selected_model
            cfg.connect_provider(provider_id, config_values)
            st.success(f"✅ {provider_cls.meta.name} connected!")
            st.rerun()

    return provider_id


def _render_custom_provider_form():
    st.markdown("### Custom OpenAI-compatible Provider")
    st.markdown("Configure any OpenAI-compatible API endpoint.")

    with st.form("custom_provider_form"):
        provider_id = st.text_input("Provider ID", placeholder="e.g. my-provider")
        name = st.text_input("Display Name", placeholder="e.g. My Provider")
        base_url = st.text_input("Base URL", placeholder="https://api.myprovider.com/v1")
        api_key = st.text_input("API Key", type="password", placeholder="API key or {env:VAR_NAME}")

        st.markdown("**Models**")
        model_ids = []
        for i in range(3):
            mid = st.text_input(f"Model {i+1}", key=f"cm_{i}", label_visibility="collapsed",
                               placeholder="gpt-4o-mini")
            if mid:
                model_ids.append(mid)

        st.markdown("**Custom Headers (optional)**")
        headers = {}
        for i in range(2):
            cols = st.columns([2, 2])
            with cols[0]:
                key = st.text_input(f"Header key {i+1}", key=f"hk_{i}",
                                   label_visibility="collapsed", placeholder="X-API-Key")
            with cols[1]:
                val = st.text_input(f"Header value {i+1}", key=f"hv_{i}",
                                   label_visibility="collapsed", placeholder="value")
            if key and val:
                headers[key] = val

        submitted = st.form_submit_button("Add Custom Provider", type="primary", use_container_width=True)

        if submitted:
            if not provider_id or not name or not base_url:
                st.error("Provider ID, Name, and Base URL are required.")
                return None
            config_data = {
                "base_url": base_url,
                "api_key": api_key,
                "models": model_ids or ["gpt-4o-mini"],
                "headers": headers,
                "model": model_ids[0] if model_ids else "gpt-4o-mini",
            }
            cfg.connect_provider(provider_id, config_data)
            st.success(f"✅ Custom provider '{name}' connected!")
            st.rerun()

    return None
