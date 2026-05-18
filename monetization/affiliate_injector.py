from __future__ import annotations

_TRIGGERS = {
    "bookshop": {"book", "author", "read", "novel", "chapter", "memoir", "biography"},
    "audible": {"listen", "audiobook", "narrator", "audio"},
    "brilliant": {"math", "mathematics", "science", "physics", "logic", "probability", "statistics", "chemistry"},
}

_LINK_TEMPLATES = {
    "bookshop": "Find books from today's episode on [Bookshop.org]({url}) — supporting independent bookstores.",
    "audible": "Prefer listening? Get the audiobook on [Audible]({url}).",
    "brilliant": "Explore these ideas interactively at [Brilliant.org]({url}) — 30 days free.",
}


def inject_affiliates(text: str, affiliates: dict[str, str]) -> str:
    if not affiliates:
        return text
    additions = []
    lower = text.lower()
    for key, url in affiliates.items():
        if not url:
            continue
        triggers = _TRIGGERS.get(key, set())
        if any(trigger in lower for trigger in triggers):
            template = _LINK_TEMPLATES.get(key, "")
            if template:
                additions.append(template.format(url=url))
    if additions:
        return text + "\n\n" + "\n\n".join(additions)
    return text
