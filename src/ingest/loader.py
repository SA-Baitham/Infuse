import os
import httpx


def ingest_file(uploaded_file, raw_dir: str) -> str | None:
    os.makedirs(raw_dir, exist_ok=True)
    path = os.path.join(raw_dir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def ingest_url(url: str, raw_dir: str) -> str | None:
    os.makedirs(raw_dir, exist_ok=True)
    try:
        r = httpx.get(url, timeout=30)
        r.raise_for_status()
        title = url.split("/")[-1].split(".")[0] or "untitled"
        path = os.path.join(raw_dir, f"{title}.md")
        content = r.text
        if "<html" in content.lower() or "<!doctype" in content.lower():
            content = f"Source: {url}\n\n> Auto-imported from web.\n\n{content}"
        with open(path, "w") as f:
            f.write(content)
        return path
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None
