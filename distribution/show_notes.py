from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)


_AFFILIATE_TRIGGERS = {
    "bookshop": {"book", "author", "read", "novel", "chapter", "memoir", "biography"},
    "audible": {"listen", "audiobook", "narrator", "audio"},
    "brilliant": {"math", "mathematics", "science", "physics", "logic", "probability", "statistics"},
}

_AFFILIATE_TEMPLATES = {
    "bookshop": "Find books from today's episode on [Bookshop.org]({url}) — supporting independent bookstores.",
    "audible": "Prefer listening? Get the audiobook on [Audible]({url}).",
    "brilliant": "Explore these ideas interactively at [Brilliant.org]({url}) — 30 days free.",
}


def _clean_script(script: str) -> str:
    return script.replace("[PAUSE]", " ").replace("  ", " ").strip()


def _inject_affiliates(text: str, affiliates: dict[str, str]) -> str:
    if not affiliates:
        return text
    additions = []
    lower = text.lower()
    for key, url in affiliates.items():
        if not url:
            continue
        triggers = _AFFILIATE_TRIGGERS.get(key, set())
        if any(t in lower for t in triggers):
            template = _AFFILIATE_TEMPLATES.get(key, "")
            if template:
                additions.append(template.format(url=url))
    return text + ("\n\n" + "\n\n".join(additions) if additions else "")


def generate_post(
    title: str,
    script: str,
    slot: str,
    published: datetime,
    affiliates: dict[str, str],
) -> str:
    date_str = published.strftime("%Y-%m-%d")
    clean = _clean_script(script)
    body = _inject_affiliates(clean, affiliates)

    return f"""---
title: "{title}"
date: {date_str}
slot: {slot}
layout: post
---

## Transcript

{body}
"""


def write_post(
    title: str,
    script: str,
    slot: str,
    published: datetime,
    affiliates: dict,
    posts_dir: str | Path,
) -> Path:
    date_str = published.strftime("%Y-%m-%d")
    slug = title.lower().replace(" ", "-").replace("—", "").replace(":", "").strip("-")[:60]
    filename = Path(posts_dir) / f"{date_str}-{slug}.md"
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(
        generate_post(title, script, slot, published, affiliates),
        encoding="utf-8",
    )
    log.info("Show notes written: %s", filename)
    return filename
