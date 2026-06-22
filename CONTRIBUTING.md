# Contributing to LLM Knowledge Base

Thanks for stopping by! This project is in its early stages and all contributions are welcome.

## How to Contribute

### Report Issues

Found a bug or have a feature request? [Open an issue](https://github.com/SA-Baitham/wiki/issues) with:
- A clear title and description
- Steps to reproduce (if bug)
- What you expected vs what happened

### Submit Code

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-idea`)
3. Make your changes
4. Run a quick sanity check: `python3 -c "from src.providers import ProviderRegistry; print('OK')"`
5. Commit (`git commit -m "add: your change"`)
6. Push (`git push origin feature/your-idea`)
7. Open a Pull Request

### Add a New Provider

Providers are plug-and-play. Create a file in `src/providers/`:

```python
from .base import BaseProvider, ConfigField, ProviderMeta

class MyProvider(BaseProvider):
    meta = ProviderMeta(
        id="my-provider",
        name="My Provider",
        icon="✨",
        description="What this provider offers",
        group="Other",  # or "Popular"
    )
    models = ["model-1", "model-2"]

    @classmethod
    def config_fields(cls):
        return [
            ConfigField(key="api_key", label="API Key", type="password"),
        ]

    def chat(self, messages, model=None, **kwargs):
        # Your LLM call here
        pass
```

Then register it in `src/providers/__init__.py`.

### Improve the Wiki Compiler

The compiler at `src/compiler.py` sends raw docs to an LLM and saves structured wiki articles. Better prompts, chunking strategies, or structured output parsing are all great improvements.

### Code Style

- Follow the existing patterns (look at neighboring files)
- No comments unless necessary
- Prefer readability over cleverness

## Project Values

- **LLM-first**: The LLM writes and maintains the wiki, not humans
- **Flat files**: Markdown + JSON, no database needed
- **Provider-agnostic**: Users should be able to use any LLM backend
- **Viewable anywhere**: Wiki files open in Obsidian, VS Code, GitHub, etc.

## Questions?

Open an issue or start a discussion. All skill levels welcome.
