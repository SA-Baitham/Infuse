import os
import glob
from src.providers import ProviderRegistry
from src import config as cfg


def generate_output(provider_id: str, output_type: str, topic: str, wiki_dir: str, output_dir: str) -> str:
    provider_cls = ProviderRegistry.get(provider_id)
    if not provider_cls:
        return ""

    pconfig = cfg.get_connected_providers().get(provider_id, {})
    provider = provider_cls.from_config(pconfig)
    os.makedirs(output_dir, exist_ok=True)

    system_prompts = {
        "Marp Slides": "Create a Marp markdown presentation. Start with '---\nmarp: true\n---'. Each slide separated by '---'.",
        "Matplotlib Visualization": "Write Python matplotlib code to visualize data related to: " + topic,
        "Summary Report": "Write a comprehensive summary report in markdown format.",
    }

    system_prompt = system_prompts.get(output_type, system_prompts["Summary Report"])

    articles = glob.glob(os.path.join(wiki_dir, "**/*.md"), recursive=True)
    context = []
    for path in sorted(articles):
        with open(path) as f:
            content = f.read()
        if topic.lower() in content.lower():
            context.append(content[:1500])

    context_text = "\n\n---\n\n".join(context[:10])

    try:
        result = provider.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Based on this wiki content, {topic}:\n\n{context_text}"},
        ], model=pconfig.get("model"))

        ext = "md"
        if output_type == "Matplotlib Visualization":
            ext = "py"
        elif output_type == "Marp Slides":
            ext = "md"

        safe_name = topic.lower().replace(" ", "-")[:40]
        output_path = os.path.join(output_dir, f"{safe_name}.{ext}")
        with open(output_path, "w") as f:
            f.write(result.strip())

        return output_path
    except Exception as e:
        return f"Generation failed: {e}"
