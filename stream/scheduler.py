"""
Runs 2 hours ahead of broadcast to ensure segments are ready.
APScheduler triggers content generation for each slot.
"""
from __future__ import annotations
import logging
from datetime import datetime
from pathlib import Path
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler

log = logging.getLogger(__name__)


def _load_config() -> dict:
    root = Path(__file__).parent.parent
    return yaml.safe_load((root / "config.yml").read_text(encoding="utf-8"))


def generate_slot(slot: str) -> None:
    from content.news_aggregator import get_top_stories, format_brief
    from content.script_writer import write_script
    from content.topic_researcher import load_topic_seeds, pick_topic, research_topic
    from content.music_selector import load_index, pick_track, mark_played, save_index, get_slot_mood
    from audio.tts_engine import render_script
    from audio.show_assembler import SegmentParts, assemble_segment
    from distribution.rss_generator import SegmentMeta, add_episode
    from distribution.show_notes import write_post
    from distribution.social_poster import post_to_mastodon
    from monetization.sponsor_manager import load_sponsors, get_spot_for_slot, render_sponsor_script

    config = _load_config()
    root = Path(__file__).parent.parent
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M")
    segment_dir = root / config['paths']['segments']
    segment_dir.mkdir(parents=True, exist_ok=True)

    log.info("Generating segment: %s at %s", slot, timestamp)

    brief = None
    topic = None
    sponsor_copy = None

    if slot in ("morning_drift", "drive"):
        stories = get_top_stories(config['feeds'])
        brief = format_brief(stories)
    elif slot == "deep_cuts":
        seeds = load_topic_seeds()
        topic = pick_topic(seeds, used=[])
        brief = research_topic(topic)

    sponsors = load_sponsors(root / "content" / "sponsors.yml")
    sponsor = get_spot_for_slot(sponsors, slot)
    if sponsor:
        sponsor_copy = render_sponsor_script(sponsor)

    script = write_script(slot=slot, brief=brief, topic=topic, sponsor_copy=sponsor_copy)

    # Render speech
    speech_path = segment_dir / f"{timestamp}_{slot}_speech.mp3"
    render_script(script, speech_path, voice=config['tts']['voice'])

    # Pick music
    music_index_path = root / config['paths']['music_index']
    music_idx = load_index(music_index_path)
    mood = get_slot_mood(slot)
    music_track = pick_track(music_idx, mood=mood)
    music_path = root / music_track['path'] if music_track else None
    if music_track:
        mark_played(music_idx, music_track['path'])
        save_index(music_idx, music_index_path)

    # Pick jingles
    jingles_dir = root / config['paths']['jingles']
    intro = next(jingles_dir.glob("intro*.mp3"), None)
    outro = next(jingles_dir.glob("outro*.mp3"), None)

    parts = SegmentParts(
        intro_jingle=intro,
        speech=speech_path,
        music=music_path,
        outro_jingle=outro,
    )
    output_path = segment_dir / f"{timestamp}_{slot}.mp3"
    assemble_segment(parts, output_path)
    speech_path.unlink(missing_ok=True)

    # Distribution
    title = f"{slot.replace('_', ' ').title()} — {now.strftime('%B %d, %Y')}"
    write_post(
        title=title,
        script=script,
        slot=slot,
        published=now,
        affiliates=config['monetization'].get('affiliates', {}),
        posts_dir=root / config['paths']['website_posts'],
    )

    feed_path = root / config['paths']['podcast_feed']
    add_episode(
        feed_path=feed_path,
        episode=SegmentMeta(
            title=title,
            description=script[:200].replace("[PAUSE]", " ").strip() + "...",
            audio_url=config['station']['stream_url'].rstrip('/') + f"/segments/{output_path.name}",
            duration_seconds=int(output_path.stat().st_size / 16000) if output_path.exists() else 0,
            published=now,
            guid=f"{timestamp}-{slot}",
        ),
        station_title=config['station']['name'],
        station_url=config['station']['website_url'],
        description=config['station']['tagline'],
    )

    stream_url = config['station']['stream_url']
    hook = script[:120].replace("[PAUSE]", "").strip() + "..."
    post_to_mastodon(title, hook, stream_url)

    log.info("Segment ready: %s", output_path)


def run_scheduler() -> None:
    config = _load_config()
    scheduler = BlockingScheduler(timezone="UTC")

    for slot, times in config['schedule'].items():
        start = times['start']
        h, m = map(int, start.split(':'))
        pre_h = (h - 2) % 24
        scheduler.add_job(
            generate_slot,
            'cron',
            hour=pre_h,
            minute=m,
            args=[slot],
            id=slot,
        )
        log.info("Scheduled %s generation at %02d:%02d UTC", slot, pre_h, m)

    log.info("Scheduler running.")
    scheduler.start()
