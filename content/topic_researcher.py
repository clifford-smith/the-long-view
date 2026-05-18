from __future__ import annotations
import random
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import yaml


def load_topic_seeds() -> list[str]:
    path = Path(__file__).parent / "topic_seeds.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data["topics"]


def pick_topic(seeds: list[str], used: list[str]) -> str:
    available = [t for t in seeds if t not in used]
    if not available:
        available = seeds
    return random.choice(available)


def scrape_page(url: str, timeout: int = 10) -> str:
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text(strip=True) for p in paragraphs)[:3000]
    except Exception:
        return ""


def _search_urls(topic: str) -> list[str]:
    wiki_slug = topic.replace(" ", "_").replace(":", "").replace("—", "")[:80]
    return [
        f"https://en.wikipedia.org/wiki/{wiki_slug}",
    ]


def build_research_brief(topic: str, findings: list[str]) -> str:
    lines = [f"RESEARCH BRIEF: {topic}", "=" * 50, ""]
    for i, finding in enumerate(findings, 1):
        if finding.strip():
            lines.append(f"SOURCE {i}:")
            lines.append(finding[:1500])
            lines.append("")
    return "\n".join(lines)


def research_topic(topic: str) -> str:
    urls = _search_urls(topic)
    findings = [scrape_page(url) for url in urls]
    findings = [f for f in findings if f]
    if not findings:
        findings = [f"Discuss {topic} based on your knowledge."]
    return build_research_brief(topic, findings)
