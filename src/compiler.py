import os
import glob
from src.providers import ProviderRegistry
from src import config as cfg


def compile_to_wiki(provider_id: str, model: str, raw_dir: str, wiki_dir: str) -> int:
    provider_cls = ProviderRegistry.get(provider_id)
    if not provider_cls:
        return 0

    pconfig = cfg.get_connected_providers().get(provider_id, {})
    provider = provider_cls.from_config(pconfig)

    os.makedirs(wiki_dir, exist_ok=True)

    raw_files = glob.glob(os.path.join(raw_dir, "**/*"), recursive=True)
    raw_files = [f for f in raw_files if os.path.isfile(f)]

    if not raw_files:
        return 0

    articles_created = 0

    for filepath in raw_files:
        with open(filepath, errors="ignore") as f:
            content = f.read()

        if not content.strip():
            continue

        system_prompt = """You are a wiki compiler. Given a source document, create a well-structured wiki article in markdown format.

The article should include:
1. A title (H1)
2. A brief summary
3. Key concepts and definitions
4. Related topics / backlinks (as a list at the end)
5. Categorization tags

Output ONLY the markdown article, no other text."""

        user_prompt = f"Compile this source document into a wiki article:\n\n{content[:8000]}"

        try:
            result = provider.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ], model=model)

            basename = os.path.splitext(os.path.basename(filepath))[0]
            article_path = os.path.join(wiki_dir, f"{basename}.md")
            with open(article_path, "w") as f:
                f.write(result.strip())
            articles_created += 1
        except Exception as e:
            print(f"Failed to compile {filepath}: {e}")

    return articles_created
