from .base import BaseProvider, ConfigField, ProviderMeta


class OpenRouterProvider(BaseProvider):
    meta = ProviderMeta(
        id="openrouter",
        name="OpenRouter",
        icon="🔀",
        description="Route to 300+ models via one API — GPT, Claude, Gemini, DeepSeek, and more",
        group="Other",
    )
    models = [
        "openrouter/free",
        "openai/gpt-4o", "openai/gpt-4o-mini", "openai/o3-mini",
        "anthropic/claude-sonnet-4", "anthropic/claude-3.5-haiku",
        "google/gemini-2.5-pro-exp-03-25",
        "deepseek/deepseek-chat", "meta-llama/llama-3.3-70b-instruct",
        "mistral/mistral-large-2411", "qwen/qwen-2.5-72b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
    ]

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="api_key", label="API Key", type="password", placeholder="sk-or-...", env_var="OPENROUTER_API_KEY"),
            ConfigField(key="base_url", label="Base URL (optional)", type="text",
                       placeholder="https://openrouter.ai/api/v1", required=False),
        ]

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        import openai
        client = openai.OpenAI(
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url") or "https://openrouter.ai/api/v1",
        )
        extra_headers = {"HTTP-Referer": "https://github.com/baitham/wiki", "X-Title": "LLM Knowledge Base"}
        response = client.chat.completions.create(
            model=model or self.models[0],
            messages=messages,
            extra_headers=extra_headers,
            **kwargs,
        )
        return response.choices[0].message.content
