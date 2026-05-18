from __future__ import annotations
import yaml
from pathlib import Path

# Sponsors whose category tags intersect this set are never aired, regardless of
# their active flag. Add categories here rather than blocking individual sponsors
# so the rule stays consistent as the sponsor list grows.
BLOCKED_CATEGORIES: frozenset[str] = frozenset({
    # Anti-science / misinformation
    "anti_science",
    "climate_denial",
    "anti_vaccine",
    "misinformation",
    "pseudoscience",
    "conspiracy",
    # Anti-technology / surveillance
    "anti_technology",
    "surveillance_tech",
    # Harmful / predatory industries
    "tobacco",
    "fossil_fuel",
    "firearms",
    "gambling",
    "predatory_finance",
    "payday_loans",
    # Speculative / scam-adjacent
    "crypto",
    "nft",
    # Partisan political
    "political",
    "partisan",
})


def is_acceptable(sponsor: dict) -> bool:
    """Return False if any of the sponsor's categories are blocked."""
    categories = {c.lower() for c in sponsor.get("categories", [])}
    return categories.isdisjoint(BLOCKED_CATEGORIES)


def load_sponsors(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("sponsors", [])


def get_spot_for_slot(sponsors: list[dict], slot: str) -> dict | None:
    eligible = [
        s for s in sponsors
        if s.get("active") and slot in s.get("slots", []) and is_acceptable(s)
    ]
    return eligible[0] if eligible else None


def render_sponsor_script(sponsor: dict) -> str:
    return sponsor.get("copy", "")
