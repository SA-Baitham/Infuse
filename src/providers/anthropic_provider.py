from .base import BaseProvider, ConfigField, ProviderMeta
import httpx


class AnthropicProvider(BaseProvider):
    meta = ProviderMeta(
        id="anthropic",
        name="Anthropic",
        icon="🟣",
        tag="Recommended",
        description="Claude Sonnet, Haiku, Opus — best for knowledge work",
        group="Popular",
    )
    models = [
        "claude-sonnet-4-20250514", "claude-3-5-haiku-20241022",
        "claude-opus-4-20250514", "claude-3-5-sonnet-20241022",
    ]

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="api_key", label="API Key", type="password", placeholder="sk-ant-...", env_var="ANTHROPIC_API_KEY"),
        ]

    @classmethod
    def fetch_models(cls, config: dict) -> list[str] | None:
        api_key = config.get("api_key")
        if not api_key:
            return None
        try:
            r = httpx.get(
                "https://api.anthropic.com/v1/models",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                timeout=10,
            )
            r.raise_for_status()
            models = [m["id"] for m in r.json().get("data", [])]
            return sorted(models) if models else None
        except Exception:
            return None

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.config.get("api_key"))
        system = None
        msgs = messages
        if messages and messages[0].get("role") == "system":
            system = messages[0]["content"]
            msgs = messages[1:]
        response = client.messages.create(
            model=model or self.models[0],
            system=system,
            messages=msgs,
            max_tokens=kwargs.get("max_tokens", 8192),
        )
        return response.content[0].text
