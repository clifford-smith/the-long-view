import pytest
from unittest.mock import patch, MagicMock
from content.topic_researcher import (
    load_topic_seeds, pick_topic, scrape_page, build_research_brief
)


def test_load_topic_seeds_returns_list():
    seeds = load_topic_seeds()
    assert isinstance(seeds, list)
    assert len(seeds) >= 10
    assert all(isinstance(t, str) for t in seeds)


def test_pick_topic_returns_string():
    seeds = ["Topic A", "Topic B", "Topic C"]
    topic = pick_topic(seeds, used=[])
    assert topic in seeds


def test_pick_topic_avoids_used():
    seeds = ["Topic A", "Topic B"]
    topic = pick_topic(seeds, used=["Topic A"])
    assert topic == "Topic B"


def test_pick_topic_resets_when_all_used():
    seeds = ["Topic A", "Topic B"]
    topic = pick_topic(seeds, used=["Topic A", "Topic B"])
    assert topic in seeds


def test_scrape_page_returns_text():
    mock_response = MagicMock()
    mock_response.text = "<html><body><p>Interesting content here.</p></body></html>"
    mock_response.raise_for_status = MagicMock()
    with patch("requests.get", return_value=mock_response):
        text = scrape_page("https://example.com/article")
    assert "Interesting content" in text


def test_scrape_page_handles_failure():
    with patch("requests.get", side_effect=Exception("timeout")):
        text = scrape_page("https://bad-url.com")
    assert text == ""


def test_build_research_brief_structures_findings():
    findings = ["Clocks were invented in medieval Europe.", "Sundials predate mechanical clocks."]
    brief = build_research_brief("The history of timekeeping", findings)
    assert "timekeeping" in brief.lower()
    assert "Clocks" in brief or "mechanical" in brief
