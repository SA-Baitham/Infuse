# Infuse

A Streamlit-powered personal knowledge base system. LLMs ingest source documents, compile them into a structured wiki of markdown files, and enable Q&A, health checks, and visual output generation.

## Workflow

```
Source docs (articles, papers, repos)
        │
        ▼  Obsidian Web Clipper / upload
   data/raw/
        │
        ▼  LLM compilation
   data/wiki/  ←  Structured .md articles with backlinks
        │
        ├── Q&A        — Ask complex questions against the wiki
        ├── Health     — Find inconsistencies, suggest connections
        ├── Output     — Generate Marp slides, visualizations, reports
        └── Search     — Full-text search over all articles
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add API keys
streamlit run app.py
```

## Providers

| Provider | Type | Env Var |
|----------|------|---------|
| Anthropic (Recommended) | API key | `ANTHROPIC_API_KEY` |
| OpenAI | API key | `OPENAI_API_KEY` |
| Google Gemini | API key | `GEMINI_API_KEY` |
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| NVIDIA | API key | `NVIDIA_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_API_KEY` |
| Ollama | local URL | `OLLAMA_BASE_URL` |

Providers with env vars set are auto-detected on startup.

## Pages

- **Dashboard** — Wiki stats, connected providers, quick actions
- **Ingest** — Upload files or import URLs, compile raw → wiki via LLM
- **Wiki** — Browse compiled articles with markdown rendering
- **Q&A** — Ask questions against the wiki with source citations
- **Output** — Generate Marp slides, matplotlib visualizations, summary reports
- **Health** — LLM-powered linting: inconsistencies, connections, article suggestions
- **Settings** — Kilo-style provider management (add, configure, disconnect)

## Architecture

```
wiki/
├── app.py                  # Streamlit entry point
├── src/
│   ├── providers/          # Plugin-based provider system
│   │   ├── base.py         # BaseProvider ABC, ProviderRegistry
│   │   └── *_provider.py   # One file per provider
│   ├── ui/
│   │   ├── components.py   # Kilo-style provider selection/connection
│   │   ├── pages.py        # Page renderers
│   │   └── styles.py       # Dark theme CSS
│   ├── ingest/loader.py    # File upload + URL import
│   ├── compiler.py         # Raw → wiki compilation
│   ├── qa.py               # Wiki-grounded Q&A
│   ├── health.py           # Wiki linting
│   ├── output.py           # Output generators
│   └── search.py           # Full-text search index
├── data/
│   ├── raw/                # Source documents
│   ├── wiki/               # Compiled wiki (.md)
│   └── config.json         # Provider configs
└── requirements.txt
```

The provider system follows the Kilo Code pattern: providers are registered via `ProviderRegistry`, the UI discovers them automatically, and connection dialogs render dynamic fields based on `config_fields()`.
