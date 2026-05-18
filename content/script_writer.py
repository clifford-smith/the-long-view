from __future__ import annotations
from pathlib import Path
import ollama
import yaml


def _load_config() -> dict:
    root = Path(__file__).parent.parent
    return yaml.safe_load((root / "config.yml").read_text(encoding="utf-8"))


def load_prompt(slot: str) -> str:
    config = _load_config()
    prompts_dir = Path(__file__).parent.parent / config['paths']['prompts']
    base = (prompts_dir / "aria_base.txt").read_text(encoding="utf-8")
    slot_file = prompts_dir / f"{slot}.txt"
    slot_text = slot_file.read_text(encoding="utf-8") if slot_file.exists() else ""
    return f"{base}\n\n{slot_text}".strip()


def inject_sponsor_spot(script: str, sponsor_copy: str) -> str:
    """Insert sponsor copy at the midpoint of the script."""
    parts = script.split("[PAUSE]")
    if len(parts) < 3:
        return script + f"\n\n[PAUSE]\n\n{sponsor_copy}"
    mid = max(1, len(parts) // 2)
    parts.insert(mid, sponsor_copy)
    return "[PAUSE]".join(parts)


def write_script(
    slot: str,
    brief: str | None = None,
    topic: str | None = None,
    sponsor_copy: str | None = None,
) -> str:
    config = _load_config()
    system_prompt = load_prompt(slot)

    parts = [f"Write a radio script for the {slot.replace('_', ' ').title()} segment."]
    if brief:
        parts.append(f"\n\nCONTENT TO COVER:\n{brief}")
    if topic:
        parts.append(f"\n\nDEEP DIVE TOPIC: {topic}")
    parts.append(
        "\n\nTarget: 4–6 minutes of spoken content (~600–900 words). "
        "Include [PAUSE] markers where natural pauses occur. "
        "No stage directions. No markdown. Plain spoken English only."
    )

    response = ollama.chat(
        model=config['llm']['model'],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "".join(parts)},
        ],
    )
    script = response["message"]["content"]

    if sponsor_copy:
        script = inject_sponsor_spot(script, sponsor_copy)

    return script
