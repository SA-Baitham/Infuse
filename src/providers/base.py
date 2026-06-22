from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


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
