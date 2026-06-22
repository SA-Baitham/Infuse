import os
import glob
from src.providers import ProviderRegistry
from src import config as cfg


def run_health_check(provider_id: str, check_type: str, wiki_dir: str) -> str:
    provider_cls = ProviderRegistry.get(provider_id)
    if not provider_cls:
        return "Provider not found."

    pconfig = cfg.get_connected_providers().get(provider_id, {})
    provider = provider_cls.from_config(pconfig)

    articles = glob.glob(os.path.join(wiki_dir, "**/*.md"), recursive=True)
    if not articles:
        return "No wiki articles found."

    summaries = []
    for path in sorted(articles)[:30]:
        with open(path) as f:
            content = f.read()
        rel_path = os.path.relpath(path, wiki_dir)
        first_line = content.split("\n")[0] if content else "Untitled"
        word_count = len(content.split())
        summaries.append(f"- {rel_path}: {first_line} ({word_count} words)")

    summary_text = "\n".join(summaries)

    prompts = {
        "Full health check": "Review this wiki and identify: 1) Inconsistencies, 2) Missing cross-references, 3) Opportunities for new articles, 4) Data quality issues.",
        "Find inconsistencies": "Identify contradictory information, outdated content, or formatting inconsistencies across these articles.",
        "Find interesting connections": "Suggest interesting cross-connections between articles that aren't currently linked.",
        "Suggest new article candidates": "Based on the existing content, suggest 3-5 new article topics that would fill gaps in the knowledge base.",
    }

    prompt = prompts.get(check_type, prompts["Full health check"])

    try:
        result = provider.chat([
            {"role": "system", "content": "You are a wiki quality analyst. Be thorough and specific."},
            {"role": "user", "content": f"Wiki articles:\n\n{summary_text}\n\n{prompt}"},
        ], model=pconfig.get("model"))
        return result
    except Exception as e:
        return f"Health check failed: {e}"
