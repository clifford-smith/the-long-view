from __future__ import annotations
import re
import feedparser
from datetime import datetime
from difflib import SequenceMatcher
from dataclasses import dataclass


@dataclass
class Story:
    title: str
    summary: str
    source: str
    published: datetime
    url: str


_INTEREST_KEYWORDS = {
    'research', 'discovery', 'study', 'history', 'science', 'art',
    'culture', 'philosophy', 'technology', 'economics', 'climate',
    'language', 'mathematics', 'biology', 'psychology', 'archaeology',
}


def fetch_feed(url: str, source_name: str) -> list[Story]:
    try:
        feed = feedparser.parse(url)
        stories = []
        for entry in feed.entries[:10]:
            parsed = getattr(entry, 'published_parsed', None)
            published = datetime(*parsed[:6]) if parsed else datetime.now()
            summary = (getattr(entry, 'summary', None) or getattr(entry, 'description', '') or '')[:500]
            stories.append(Story(
                title=getattr(entry, 'title', ''),
                summary=summary,
                source=source_name,
                published=published,
                url=getattr(entry, 'link', ''),
            ))
        return stories
    except Exception:
        return []


def deduplicate(stories: list[Story], threshold: float = 0.72) -> list[Story]:
    unique: list[Story] = []
    for story in stories:
        is_dupe = any(
            SequenceMatcher(None, story.title.lower(), u.title.lower()).ratio() > threshold
            for u in unique
        )
        if not is_dupe:
            unique.append(story)
    return unique


def score_story(story: Story) -> float:
    age_seconds = (datetime.now() - story.published).total_seconds()
    recency = max(0.0, 1.0 - age_seconds / 86400)
    text = (story.title + ' ' + story.summary).lower()
    keyword_hits = sum(1 for kw in _INTEREST_KEYWORDS if re.search(r'\b' + kw + r'\b', text))
    interest = keyword_hits / len(_INTEREST_KEYWORDS)
    return recency * 0.6 + interest * 0.4


def format_brief(stories: list[Story]) -> str:
    lines = ["TODAY'S BRIEF\n" + "=" * 40]
    for i, s in enumerate(stories, 1):
        lines.append(f"\n{i}. [{s.source}] {s.title}")
        lines.append(f"   {s.summary[:250]}")
    return "\n".join(lines)


def get_top_stories(feeds: list[dict], n: int = 5) -> list[Story]:
    all_stories: list[Story] = []
    for feed_cfg in feeds:
        all_stories.extend(fetch_feed(feed_cfg['url'], feed_cfg['name']))
    unique = deduplicate(all_stories)
    return sorted(unique, key=score_story, reverse=True)[:n]
