import os
import glob
import json
import re

INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index.json")


def build_index(wiki_dir: str):
    index = {}
    articles = glob.glob(os.path.join(wiki_dir, "**/*.md"), recursive=True)
    for path in articles:
        with open(path) as f:
            content = f.read()
        rel_path = os.path.relpath(path, wiki_dir)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else rel_path
        words = set(re.findall(r"\w+", content.lower()))
        index[rel_path] = {
            "title": title,
            "path": rel_path,
            "words": list(words),
            "word_count": len(content.split()),
        }

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)

    return index


def search(query: str, wiki_dir: str) -> list[dict]:
    if not os.path.exists(INDEX_PATH):
        build_index(wiki_dir)

    with open(INDEX_PATH) as f:
        index = json.load(f)

    query_words = set(re.findall(r"\w+", query.lower()))
    results = []

    for path, data in index.items():
        matches = len(query_words & set(data["words"]))
        if matches > 0:
            results.append({
                "path": path,
                "title": data["title"],
                "relevance": matches / max(len(query_words), 1),
                "word_count": data["word_count"],
            })

    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:20]
