from .base import BaseProvider, ConfigField, ProviderMeta


class GeminiProvider(BaseProvider):
    meta = ProviderMeta(
        id="gemini",
        name="Google Gemini",
        icon="🔷",
        description="Gemini 2.5 Pro, Flash — large context window",
        group="Other",
    )
    models = [
        "gemini-2.5-pro-exp-03-25", "gemini-2.0-flash",
        "gemini-2.0-flash-lite", "gemini-1.5-pro",
    ]

    @classmethod
    def config_fields(cls) -> list[ConfigField]:
        return [
            ConfigField(key="api_key", label="API Key", type="password", placeholder="AIza...", env_var="GEMINI_API_KEY"),
        ]

    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        from google import genai
        client = genai.Client(api_key=self.config.get("api_key"))
        contents = []
        for m in messages:
            if m["role"] == "system":
                continue
            contents.append({
                "role": "user" if m["role"] in ("user", "system") else "model",
                "parts": [{"text": m["content"]}],
            })
        response = client.models.generate_content(
            model=model or self.models[0],
            contents=contents,
        )
        return response.text
