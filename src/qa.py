import os
import glob
from src.providers import ProviderRegistry
from src import config as cfg


def query_wiki(provider_id: str, model: str, question: str, wiki_dir: str) -> tuple[str, list[str]]:
    provider_cls = ProviderRegistry.get(provider_id)
    if not provider_cls:
        return "Provider not found.", []

    pconfig = cfg.get_connected_providers().get(provider_id, {})
    provider = provider_cls.from_config(pconfig)

    articles = glob.glob(os.path.join(wiki_dir, "**/*.md"), recursive=True)
    context_parts = []
    sources = []

    for path in sorted(articles)[:20]:
        with open(path) as f:
            content = f.read()
        rel_path = os.path.relpath(path, wiki_dir)
        context_parts.append(f"### {rel_path}\n\n{content[:2000]}")
        sources.append(rel_path)

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = """You are a research assistant with access to a wiki knowledge base.
Answer the user's question based on the provided wiki articles.
Cite your sources by mentioning the article filenames.
If the wiki doesn't contain enough information, say so clearly."""

    user_prompt = f"Wiki articles:\n\n{context[:12000]}\n\nQuestion: {question}"

    try:
        answer = provider.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ], model=model)
        return answer, sources
    except Exception as e:
        return f"Error: {e}", []
