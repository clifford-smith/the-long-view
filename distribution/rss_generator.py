from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from xml.etree import ElementTree as ET


@dataclass
class SegmentMeta:
    title: str
    description: str
    audio_url: str
    duration_seconds: int
    published: datetime
    guid: str


def generate_rss(
    episodes: list[SegmentMeta],
    station_title: str,
    station_url: str,
    description: str,
) -> str:
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = station_title
    ET.SubElement(channel, "link").text = station_url
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "language").text = "en-us"

    for ep in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep.title
        ET.SubElement(item, "description").text = ep.description
        ET.SubElement(item, "guid").text = ep.guid
        ET.SubElement(item, "pubDate").text = format_datetime(ep.published)

        enc = ET.SubElement(item, "enclosure")
        enc.set("url", ep.audio_url)
        enc.set("type", "audio/mpeg")
        enc.set("length", str(ep.duration_seconds * 16000))

        ET.SubElement(item, "itunes:duration").text = str(ep.duration_seconds)

    ET.indent(rss, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="unicode")


def add_episode(feed_path: Path, episode: SegmentMeta, **kwargs) -> None:
    """Load existing feed, prepend new episode, write back."""
    existing: list[SegmentMeta] = []
    if feed_path.exists():
        tree = ET.parse(feed_path)
        root = tree.getroot()
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item"):
                guid_el = item.find("guid")
                title_el = item.find("title")
                desc_el = item.find("description")
                enc_el = item.find("enclosure")
                pub_el = item.find("pubDate")
                dur_el = item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}duration")
                if all(el is not None for el in [guid_el, title_el, enc_el]):
                    from email.utils import parsedate_to_datetime
                    pub = parsedate_to_datetime(pub_el.text) if pub_el is not None else datetime.now()
                    existing.append(SegmentMeta(
                        title=title_el.text or "",
                        description=desc_el.text or "" if desc_el is not None else "",
                        audio_url=enc_el.get("url", ""),
                        duration_seconds=int(dur_el.text or "0") if dur_el is not None else 0,
                        published=pub,
                        guid=guid_el.text or "",
                    ))

    all_episodes = [episode] + existing
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.write_text(generate_rss(all_episodes, **kwargs), encoding="utf-8")
