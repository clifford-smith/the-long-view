from __future__ import annotations
import yaml
from pathlib import Path


def load_sponsors(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("sponsors", [])


def get_spot_for_slot(sponsors: list[dict], slot: str) -> dict | None:
    eligible = [s for s in sponsors if s.get("active") and slot in s.get("slots", [])]
    return eligible[0] if eligible else None


def render_sponsor_script(sponsor: dict) -> str:
    return sponsor.get("copy", "")
