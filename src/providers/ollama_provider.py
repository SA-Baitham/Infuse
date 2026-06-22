from .base import BaseProvider, ConfigField, ProviderMeta
import httpx


class OllamaProvider(BaseProvider):
    meta = ProviderMeta(
        id="ollama",
        name="Ollama",
        icon="🦙",
        description="Local models via Ollama — llama, mistral, qwen, etc.",
        group="Other",
    )
    models = []

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="base_url", label="Ollama Base URL", type="text",
                       placeholder="http://localhost:11434", env_var="OLLAMA_BASE_URL"),
        ]

    def _fetch_models(self):
        try:
            r = httpx.get(f"{self.config.get('base_url', 'http://localhost:11434')}/api/tags",
                         timeout=5)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return ["llama3", "mistral", "qwen2.5", "codellama"]

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        url = f"{self.config.get('base_url', 'http://localhost:11434')}/api/chat"
        payload = {
            "model": model or "llama3",
            "messages": messages,
            "stream": False,
            **{k: v for k, v in kwargs.items() if k in ("temperature", "max_tokens")},
        }
        r = httpx.post(url, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"]
