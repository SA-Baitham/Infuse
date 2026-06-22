from .base import BaseProvider, ConfigField, ProviderMeta


class OpenCodeZenProvider(BaseProvider):
    meta = ProviderMeta(
        id="opencode",
        name="OpenCode Zen",
        icon="🧘",
        tag="Curated",
        description="Curated models tested for agents — GPT-5, Claude, Gemini, Qwen, and more",
        group="Popular",
    )
    models = [
        "opencode/claude-sonnet-4-20250514",
        "opencode/claude-3-5-haiku-20241022",
        "opencode/gpt-5",
        "opencode/gpt-5-codex",
        "opencode/gpt-5-nano",
        "opencode/gpt-5.1-codex",
        "opencode/gpt-5.1-codex-max",
        "opencode/gpt-5.4",
        "opencode/gpt-5.4-mini",
        "opencode/gpt-5.4-nano",
        "opencode/gpt-5.5",
        "opencode/gpt-5.5-pro",
        "opencode/gemini-2.5-pro-exp-03-25",
        "opencode/deepseek-chat",
        "opencode/qwen-3-coder-480b",
        "opencode/big-pickle",
    ]

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="api_key", label="API Key", type="password", placeholder="oc-zen-...", env_var="OPENCODE_API_KEY"),
            ConfigField(key="base_url", label="Base URL (optional)", type="text",
                       placeholder="https://opencode.ai/zen/v1", required=False),
        ]

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        import openai
        client = openai.OpenAI(
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url") or "https://opencode.ai/zen/v1",
        )
        response = client.chat.completions.create(
            model=model or self.models[0],
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content
