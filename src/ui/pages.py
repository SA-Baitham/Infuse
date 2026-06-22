import streamlit as st
import os
import glob
from src.providers import ProviderRegistry
from src import config as cfg
from src.ui.components import render_provider_selection, render_connection_dialog
from src.ingest.loader import ingest_file, ingest_url
from src.compiler import compile_to_wiki
from src.qa import query_wiki
from src.health import run_health_check
from src.output import generate_output

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
WIKI_DIR = os.path.join(DATA_DIR, "wiki")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")


def _provider_select(providers: dict, key: str) -> str:
    """Provider selectbox defaulting to the global active provider."""
    active = st.session_state.get("active_provider")
    default_idx = 0
    provider_ids = list(providers.keys())
    if active and active in provider_ids:
        default_idx = provider_ids.index(active)
    return st.selectbox(
        "Provider",
        provider_ids,
        index=default_idx,
        format_func=lambda x: ProviderRegistry.get(x).meta.name if ProviderRegistry.get(x) else x,
        key=key,
    )


def _model_select(provider_id: str, providers: dict, key: str) -> str:
    """Model selectbox with a refresh button to fetch models from API."""
    pcls = ProviderRegistry.get(provider_id)
    pconfig = providers.get(provider_id, {})
    models = pcls.models[:] if pcls and pcls.models else pconfig.get("models", ["gpt-4o-mini"])

    refresh_key = f"refresh_{key}"
    if st.button("🔄 Refresh Models", key=refresh_key, use_container_width=True):
        with st.spinner("Fetching models..."):
            try:
                result = pcls.fetch_models(pconfig)
                if result:
                    st.session_state[refresh_key] = result
                    st.success(f"Found {len(result)} models")
                else:
                    st.warning("No models found.")
            except Exception as e:
                st.error(f"Failed: {e}")

    cached = st.session_state.get(refresh_key)
    if cached:
        models = cached
    if not models:
        models = ["gpt-4o-mini"]

    return st.selectbox("Model", models, key=key)


def render_dashboard():
    st.title("📊 Dashboard")

    raw_dir_exists = os.path.exists(RAW_DIR)
    wiki_dir_exists = os.path.exists(WIKI_DIR)

    raw_files = []
    if raw_dir_exists:
        for root, dirs, files in os.walk(RAW_DIR):
            for f in files:
                raw_files.append(os.path.join(root, f))
    raw_count = len(raw_files)
    raw_size = sum(os.path.getsize(f) for f in raw_files) / 1024 if raw_files else 0

    wiki_files_list = glob.glob(os.path.join(WIKI_DIR, "**/*.md"), recursive=True) if wiki_dir_exists else []
    wiki_count = len(wiki_files_list)
    wiki_words = sum(len(open(f).read().split()) for f in wiki_files_list) if wiki_files_list else 0

    providers = cfg.get_connected_providers()

    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{raw_count}</div>
            <div class="stat-label">Raw Documents</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{wiki_count}</div>
            <div class="stat-label">Wiki Articles</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{wiki_words:,}</div>
            <div class="stat-label">Total Words</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(providers)}</div>
            <div class="stat-label">Connected Providers</div>
        </div>
        """, unsafe_allow_html=True)

    if raw_files:
        st.markdown(f"📁 `data/raw/` — {raw_size:.1f} KB total")
    if wiki_files_list:
        avg_words = wiki_words // wiki_count if wiki_count else 0
        st.markdown(f"📁 `data/wiki/` — ~{avg_words} words per article")

    st.divider()
    st.subheader("Connected Providers")
    if providers:
        for pid, pconfig in providers.items():
            pcls = ProviderRegistry.get(pid)
            name = pcls.meta.name if pcls else pid
            icon = pcls.meta.icon if pcls else "🔌"
            model = pconfig.get("model", "unknown")
            from_env = pconfig.get("_from_env", False)
            tag = " ⚡ from .env" if from_env else ""
            st.markdown(f"- {icon} **{name}** → model: `{model}`{tag}")
    else:
        st.info("No providers connected. Go to **Settings** to add one.")

    active = st.session_state.get("active_provider")
    if active and active in providers:
        pcls = ProviderRegistry.get(active)
        name = pcls.meta.name if pcls else active
        st.info(f"🟢 Active provider: **{name}** — set in sidebar")

    st.divider()
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Ingest Documents", use_container_width=True):
            st.session_state.page = "Ingest"
    with col2:
        if st.button("❓ Ask a Question", use_container_width=True):
            st.session_state.page = "Q&A"
    with col3:
        if st.button("🏥 Health Check", use_container_width=True):
            st.session_state.page = "Health"


def render_ingest():
    st.title("📥 Data Ingestion")
    st.markdown("Import source documents to be compiled into the wiki.")

    providers = cfg.get_connected_providers()
    if not providers:
        st.warning("No providers connected. Go to **Settings** to add one first.")
        return

    tab1, tab2 = st.tabs(["Upload Files", "Import from URL"])

    with tab1:
        uploaded = st.file_uploader(
            "Upload markdown files",
            type=["md", "txt", "pdf"],
            accept_multiple_files=True,
        )
        if uploaded:
            for f in uploaded:
                ingest_file(f, RAW_DIR)
            st.success(f"✅ {len(uploaded)} file(s) saved to raw/")

    with tab2:
        url = st.text_input("URL to import (e.g. Obsidian Web Clipper output)")
        if url:
            if st.button("Import URL"):
                with st.spinner("Fetching..."):
                    result = ingest_url(url, RAW_DIR)
                    if result:
                        st.success(f"✅ Imported: {result}")
                    else:
                        st.error("Failed to import URL")

    st.divider()
    st.subheader("Compile to Wiki")
    st.markdown("Select a provider and model to compile raw documents into wiki articles.")

    provider_id = _provider_select(providers, "ingest_provider")
    if provider_id:
        model = _model_select(provider_id, providers, "ingest_model")

        if st.button("🚀 Compile Raw → Wiki", type="primary", use_container_width=True):
            with st.spinner("Compiling wiki articles from raw documents..."):
                result = compile_to_wiki(provider_id, model, RAW_DIR, WIKI_DIR)
            if result:
                st.success(f"✅ Wiki compiled! {result} articles created.")
            else:
                st.error("Compilation failed or no raw documents found.")


def render_wiki():
    st.title("📚 Wiki Browser")
    st.markdown("Browse compiled wiki articles.")

    if not os.path.exists(WIKI_DIR):
        st.info("No wiki articles yet. Ingest some documents and compile them first.")
        return

    articles = glob.glob(os.path.join(WIKI_DIR, "**/*.md"), recursive=True)
    if not articles:
        st.info("No wiki articles found.")
        return

    article_paths = {os.path.relpath(a, WIKI_DIR): a for a in sorted(articles)}
    selected = st.selectbox("Select article", list(article_paths.keys()))

    if selected:
        path = article_paths[selected]
        with open(path) as f:
            content = f.read()
        st.markdown(content)

        with st.expander("Article Info"):
            st.markdown(f"- **Path:** `{selected}`")
            st.markdown(f"- **Size:** {len(content)} chars, {len(content.split())} words")


def render_qa():
    st.title("❓ Q&A")
    st.markdown("Ask complex questions against your wiki knowledge base.")

    providers = cfg.get_connected_providers()
    if not providers:
        st.warning("No providers connected. Go to **Settings** to add one first.")
        return

    if not os.path.exists(WIKI_DIR) or not glob.glob(os.path.join(WIKI_DIR, "**/*.md"), recursive=True):
        st.info("No wiki articles yet. Ingest and compile documents first.")
        return

    provider_id = _provider_select(providers, "qa_provider")
    model = _model_select(provider_id, providers, "qa_model")

    question = st.text_area("Your question",
                           placeholder="e.g. What are the key concepts and connections in this research area?",
                           height=100)

    if question and st.button("Ask", type="primary", use_container_width=True):
        with st.spinner("Researching your question against the wiki..."):
            answer, sources = query_wiki(provider_id, model, question, WIKI_DIR)

        st.markdown("### Answer")
        st.markdown(f'<div class="chat-message assistant">{answer}</div>', unsafe_allow_html=True)

        if sources:
            with st.expander("Sources"):
                for s in sources:
                    st.markdown(f"- {s}")

        if st.button("💾 Save answer as wiki article"):
            title = question[:60].strip()
            safe_name = title.lower().replace(" ", "-")[:40]
            article_path = os.path.join(WIKI_DIR, f"qa-{safe_name}.md")
            with open(article_path, "w") as f:
                f.write(f"# {title}\n\n**Question:** {question}\n\n{answer}\n")
            st.success(f"✅ Saved to wiki: {article_path}")


def render_health():
    st.title("🏥 Health Check")
    st.markdown("Run LLM-powered health checks over the wiki.")

    providers = cfg.get_connected_providers()
    if not providers:
        st.warning("No providers connected. Go to **Settings** to add one first.")
        return

    if not os.path.exists(WIKI_DIR) or not glob.glob(os.path.join(WIKI_DIR, "**/*.md"), recursive=True):
        st.info("No wiki articles yet.")
        return

    provider_id = _provider_select(providers, "health_provider")
    model = _model_select(provider_id, providers, "health_model")

    check_type = st.selectbox("Check type", [
        "Full health check",
        "Find inconsistencies",
        "Find interesting connections",
        "Suggest new article candidates",
    ])

    if st.button("🔍 Run Check", type="primary", use_container_width=True):
        with st.spinner("Running health check..."):
            results = run_health_check(provider_id, check_type, WIKI_DIR, model)
        st.markdown("### Results")
        st.markdown(results)


def render_output():
    st.title("🎨 Output Generation")
    st.markdown("Generate visual outputs from wiki content.")

    providers = cfg.get_connected_providers()
    if not providers:
        st.warning("No providers connected. Go to **Settings** to add one first.")
        return

    if not os.path.exists(WIKI_DIR) or not glob.glob(os.path.join(WIKI_DIR, "**/*.md"), recursive=True):
        st.info("No wiki articles yet.")
        return

    output_type = st.selectbox("Output format", [
        "Marp Slides",
        "Matplotlib Visualization",
        "Summary Report",
    ])

    topic = st.text_input("Topic or question", placeholder="What should this output be about?")

    provider_id = _provider_select(providers, "output_provider")
    model = _model_select(provider_id, providers, "output_model")

    if topic and st.button("Generate", type="primary", use_container_width=True):
        with st.spinner(f"Generating {output_type}..."):
            result = generate_output(provider_id, output_type, topic, WIKI_DIR, OUTPUT_DIR, model)
        st.success(f"✅ Output saved to: {result}")
        if os.path.exists(result):
            with open(result) as f:
                content = f.read()
            st.markdown(content)


def render_settings():
    st.title("⚙️ Settings")
    st.markdown("Manage LLM providers — add, configure, or disconnect them.")

    connected = cfg.get_connected_providers()

    st.subheader("Connected Providers")
    if connected:
        for pid, pconfig in list(connected.items()):
            pcls = ProviderRegistry.get(pid)
            icon = pcls.meta.icon if pcls else "🔌"
            name = pcls.meta.name if pcls else pid
            from_env = pconfig.get("_from_env", False)
            label = f"{icon} {name}" + (" ⚡ from .env" if from_env else "")
            with st.expander(label):
                st.json({k: v for k, v in pconfig.items() if k != "_from_env"})
                if from_env:
                    st.info("Auto-detected from environment variables.")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save to Config", key=f"save_{pid}", use_container_width=True):
                            saved = {k: v for k, v in pconfig.items() if k != "_from_env"}
                            cfg.connect_provider(pid, saved)
                            st.rerun()
                    with col2:
                        st.button("Skip", key=f"skip_{pid}", disabled=True, use_container_width=True)
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Disconnect", key=f"disconnect_{pid}", use_container_width=True):
                            cfg.disconnect_provider(pid)
                            st.rerun()
                    with col2:
                        if st.button("Test Connection", key=f"test_{pid}", use_container_width=True):
                            st.info("Connection test not yet implemented.")
    else:
        st.info("No providers connected yet.")

    st.divider()
    st.subheader("Add New Provider")

    selected = render_provider_selection()
    if selected:
        st.divider()
        render_connection_dialog(selected)
