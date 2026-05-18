import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from content.news_aggregator import (
    Story, fetch_feed, deduplicate, score_story, format_brief
)


def _mock_entry(title, summary="A summary.", published=(2026, 5, 17, 12, 0, 0, 0, 0, 0), link="https://example.com"):
    entry = MagicMock()
    entry.title = title
    entry.summary = summary
    entry.published_parsed = published
    entry.link = link
    return entry


def test_fetch_feed_returns_stories():
    mock_feed = MagicMock()
    mock_feed.entries = [_mock_entry("Test Story")]
    with patch("feedparser.parse", return_value=mock_feed):
        stories = fetch_feed("https://example.com/feed", "Test Source")
    assert len(stories) == 1
    assert stories[0].title == "Test Story"
    assert stories[0].source == "Test Source"


def test_fetch_feed_handles_failure():
    with patch("feedparser.parse", side_effect=Exception("network error")):
        stories = fetch_feed("https://bad-url.com/feed", "Bad Source")
    assert stories == []


def test_fetch_feed_caps_at_ten():
    mock_feed = MagicMock()
    mock_feed.entries = [_mock_entry(f"Story {i}") for i in range(20)]
    with patch("feedparser.parse", return_value=mock_feed):
        stories = fetch_feed("https://example.com/feed", "Source")
    assert len(stories) == 10


def test_deduplicate_removes_similar_titles():
    stories = [
        Story("Breaking: Earthquake hits Turkey", "...", "BBC", datetime.now(), ""),
        Story("Breaking: Earthquake strikes Turkey", "...", "Reuters", datetime.now(), ""),
        Story("Python 4.0 released with major changes", "...", "HN", datetime.now(), ""),
    ]
    unique = deduplicate(stories)
    assert len(unique) == 2


def test_deduplicate_keeps_distinct_stories():
    stories = [
        Story("Earthquake hits Turkey", "...", "BBC", datetime.now(), ""),
        Story("Mars mission launches successfully", "...", "NASA", datetime.now(), ""),
        Story("New study on sleep deprivation", "...", "Nature", datetime.now(), ""),
    ]
    unique = deduplicate(stories)
    assert len(unique) == 3


def test_score_prefers_recent():
    recent = Story("Science discovery made", "new research published", "Nature", datetime.now(), "")
    old = Story("Old science discovery", "old research published", "Nature", datetime(2026, 1, 1), "")
    assert score_story(recent) > score_story(old)


def test_format_brief_contains_all_stories():
    stories = [
        Story("Story One", "Summary one.", "BBC", datetime.now(), ""),
        Story("Story Two", "Summary two.", "Reuters", datetime.now(), ""),
    ]
    brief = format_brief(stories)
    assert "Story One" in brief
    assert "Story Two" in brief
    assert "BBC" in brief
    assert "Reuters" in brief
