from __future__ import annotations
import json
import random
from pathlib import Path


_SLOT_MOODS = {
    "morning_drift": "calm",
    "the_stack": "focused",
    "midday": "light",
    "deep_cuts": "ambient",
    "drive": "warm",
    "night_school": "contemplative",
    "archive": "ambient",
}

_MOOD_FALLBACKS = {
    "focused": "calm",
    "contemplative": "ambient",
    "warm": "light",
    "light": "calm",
}

_RECENTLY_PLAYED_WINDOW = 20


def load_index(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_index(idx: dict, path: Path) -> None:
    path.write_text(json.dumps(idx, indent=2), encoding="utf-8")


def get_slot_mood(slot: str) -> str:
    return _SLOT_MOODS.get(slot, "ambient")


def pick_track(idx: dict, mood: str) -> dict | None:
    recent = set(idx.get("recently_played", []))
    candidates = [t for t in idx["tracks"] if t["mood"] == mood and t["path"] not in recent]
    if not candidates:
        fallback_mood = _MOOD_FALLBACKS.get(mood, "ambient")
        candidates = [t for t in idx["tracks"] if t["mood"] in (mood, fallback_mood)]
    if not candidates:
        candidates = idx["tracks"]
    return random.choice(candidates) if candidates else None


def mark_played(idx: dict, path: str) -> None:
    recent = idx.setdefault("recently_played", [])
    if path not in recent:
        recent.append(path)
    if len(recent) > _RECENTLY_PLAYED_WINDOW:
        idx["recently_played"] = recent[-_RECENTLY_PLAYED_WINDOW:]
