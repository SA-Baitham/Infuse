import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.json")

DEFAULT_CONFIG = {
    "providers": {},
    "default_model": {},
}

_ENV_PROVIDER_CACHE = None


def _detect_env_providers() -> dict[str, dict]:
    """Auto-detect providers whose env vars are set."""
    from src.providers import ProviderRegistry
    detected = {}
    for pcls in ProviderRegistry.all():
        config = {}
        for field in pcls.config_fields():
            if field.env_var:
                val = os.environ.get(field.env_var, "")
                if val:
                    config[field.key] = val
        if config:
            config["model"] = pcls.models[0] if pcls.models else "default"
            config["_from_env"] = True
            detected[pcls.meta.id] = config
    return detected


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_connected_providers() -> dict[str, dict]:
    cfg = load_config()
    saved = cfg.get("providers", {})
    env_detected = _detect_env_providers()
    # Merge: env-detected providers are shown alongside saved ones,
    # but saved config overrides env vars when both exist
    merged = dict(env_detected)
    merged.update(saved)
    # Remove _from_env flag for saved providers that were also env-detected
    for pid, pconfig in merged.items():
        if pid in saved:
            pconfig.pop("_from_env", None)
    return merged


def connect_provider(provider_id: str, config: dict):
    cfg = load_config()
    cfg.setdefault("providers", {})[provider_id] = config
    save_config(cfg)


def disconnect_provider(provider_id: str):
    cfg = load_config()
    cfg.get("providers", {}).pop(provider_id, None)
    save_config(cfg)


def get_default_model(provider_id: str) -> str | None:
    cfg = load_config()
    return cfg.get("default_model", {}).get(provider_id)


def set_default_model(provider_id: str, model: str):
    cfg = load_config()
    cfg.setdefault("default_model", {})[provider_id] = model
    save_config(cfg)
