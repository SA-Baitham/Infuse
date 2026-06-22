from .base import BaseProvider, ConfigField, ProviderMeta, fetch_openai_compatible_models


class OpenAIProvider(BaseProvider):
    meta = ProviderMeta(
        id="openai",
        name="OpenAI",
        icon="⚡",
        tag="Popular",
        description="GPT-4o, GPT-4o mini, o3, and more",
        group="Popular",
    )
    models = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4",
        "o3-mini", "o1", "o1-mini",
    ]

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="api_key", label="API Key", type="password", placeholder="sk-...", env_var="OPENAI_API_KEY"),
            ConfigField(key="base_url", label="Base URL (optional)", type="text",
                       placeholder="https://api.openai.com/v1", required=False),
        ]

    @classmethod
    def fetch_models(cls, config: dict) -> list[str] | None:
        base = config.get("base_url") or "https://api.openai.com/v1"
        return fetch_openai_compatible_models(base, config.get("api_key"))

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        import openai
        client = openai.OpenAI(
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url") or None,
        )
        response = client.chat.completions.create(
            model=model or self.models[0],
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content
