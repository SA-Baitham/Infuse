from .base import BaseProvider, ConfigField, ProviderMeta


class NVIDIAProvider(BaseProvider):
    meta = ProviderMeta(
        id="nvidia",
        name="NVIDIA",
        icon="🔮",
        description="NVIDIA NIM — Llama, Nemotron, Mistral, and custom models at build.nvidia.com",
        group="Other",
    )
    models = [
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.1-70b-instruct",
        "mistralai/mistral-large-2411",
        "google/gemma-2-27b-it",
        "microsoft/phi-3-medium-128k-instruct",
    ]

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="api_key", label="API Key", type="password", placeholder="nvapi-...", env_var="NVIDIA_API_KEY"),
            ConfigField(key="base_url", label="Base URL (optional)", type="text",
                       placeholder="https://integrate.api.nvidia.com/v1", required=False),
        ]

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        import openai
        client = openai.OpenAI(
            api_key=self.config.get("api_key"),
            base_url=self.config.get("base_url") or "https://integrate.api.nvidia.com/v1",
        )
        response = client.chat.completions.create(
            model=model or self.models[0],
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content
