from __future__ import annotations
import os
import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

CONFIG_PATH = Path(__file__).parent.parent / "config.toml"

def _expand(path: str) -> Path:
    return Path(path).expanduser().resolve()

def load() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        raw = tomllib.load(f)
    # Expand paths
    raw["memory"]["db_path"] = str(_expand(raw["memory"]["db_path"]))
    raw["execution"]["workspace"] = str(_expand(raw["execution"]["workspace"]))
    raw["logging"]["log_file"] = str(_expand(raw["logging"]["log_file"]))
    # Ensure dirs exist
    Path(raw["memory"]["db_path"]).parent.mkdir(parents=True, exist_ok=True)
    Path(raw["execution"]["workspace"]).mkdir(parents=True, exist_ok=True)
    Path(raw["logging"]["log_file"]).parent.mkdir(parents=True, exist_ok=True)
    return raw

CFG = load()
