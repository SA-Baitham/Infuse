from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal
import httpx


@dataclass
class ConfigField:
    key: str
    label: str
    type: Literal["text", "password", "select", "multiline"]
    options: list[str] | None = None
    placeholder: str = ""
    required: bool = True
    env_var: str | None = None


@dataclass
class ProviderMeta:
    id: str
    name: str
    icon: str
    tag: str | None = None
    description: str = ""
    group: str = "Other"


class BaseProvider(ABC):
    meta: ProviderMeta
    models: list[str] = []

    def __init__(self, config: dict):
        self.config = config

    @classmethod
    @abstractmethod
    def config_fields(cls) -> list[ConfigField]:
        ...

    @abstractmethod
    def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        ...

    @classmethod
    def from_config(cls, config: dict) -> "BaseProvider":
        return cls(config)

    @classmethod
    def fetch_models(cls, config: dict) -> list[str] | None:
        """Fetch available models from the provider's API.
        Override in subclasses. Returns list of model IDs or None."""
        return None


def fetch_openai_compatible_models(base_url: str, api_key: str | None = None) -> list[str] | None:
    """Fetch models from an OpenAI-compatible /v1/models endpoint."""
    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        url = base_url.rstrip("/") + "/models"
        r = httpx.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        models = [m["id"] for m in data.get("data", [])]
        return sorted(models) if models else None
    except Exception:
        return None


class ProviderRegistry:
    _providers: dict[str, type[BaseProvider]] = {}

    @classmethod
    def register(cls, provider_cls: type[BaseProvider]):
        cls._providers[provider_cls.meta.id] = provider_cls

    @classmethod
    def all(cls) -> list[type[BaseProvider]]:
        return list(cls._providers.values())

    @classmethod
    def get(cls, provider_id: str) -> type[BaseProvider] | None:
        return cls._providers.get(provider_id)

    @classmethod
    def popular(cls) -> list[type[BaseProvider]]:
        return [p for p in cls.all() if p.meta.group == "Popular"]

    @classmethod
    def other(cls) -> list[type[BaseProvider]]:
        return [p for p in cls.all() if p.meta.group == "Other"]
