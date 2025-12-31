import os
from pathlib import Path
from typing import Optional
import tomlkit

CONFIG_FILE = Path.home() / ".config" / "avd" / "avd.toml"

def load_config() -> dict:
    if CONFIG_FILE.exists():
        return tomlkit.parse(CONFIG_FILE.read_text())
    return {}

def save_config(config: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(tomlkit.dumps(config))

def get_default_avd() -> Optional[str]:
    config = load_config()
    return config.get("default_avd")

def set_default_avd(name: str):
    config = load_config()
    config["default_avd"] = name
    save_config(config)
