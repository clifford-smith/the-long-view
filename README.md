# The Long View

**A fully autonomous 24/7 AI radio station.** No presenters, no playlist management, no manual scheduling — just an AI personality called Aria generating original content around the clock, broadcasting live, and publishing a podcast feed automatically.

---

## What it does

Every two hours, the station wakes up and generates the next programme slot:

1. **Fetches real news** from 10 RSS feeds (BBC, Reuters, Hacker News, Quanta, Aeon, and more)
2. **Writes a script** using a local LLM (Gemma 4 via Ollama) in Aria's voice — curious, thoughtful, unhurried
3. **Renders speech** using Microsoft's edge-tts (en-US-AriaNeural), free and indistinguishable from a real broadcaster
4. **Assembles the segment** — intro music, voiced content, outro — with FFmpeg and EBU R128 loudnorm
5. **Writes show notes** as a Jekyll blog post and updates the podcast RSS feed
6. **Posts to Mastodon** (optional) and reads out sponsor copy if any sponsors are active

Liquidsoap picks up each new segment automatically and streams it via Icecast2. The podcast feed is served from GitHub Pages. The whole thing runs on a single VM with no paid APIs.

---

## Architecture

```
RSS Feeds ──► news_aggregator ──► script_writer (Ollama/Gemma 4)
                                        │
                                   tts_engine (edge-tts + FFmpeg)
                                        │
                                  show_assembler (FFmpeg loudnorm)
                                        │
                         ┌─────────────┴─────────────┐
                    Icecast2 stream            podcast/feed.xml
                    (Liquidsoap)               (GitHub Pages)
```

| Layer | Technology |
|-------|-----------|
| LLM | Ollama + Gemma 4 E4B (`gemma4:e4b`, ~9 GB RAM) |
| TTS | edge-tts `en-US-AriaNeural` (free, no API key) |
| Audio processing | FFmpeg with EBU R128 loudnorm |
| Streaming | Icecast2 + Liquidsoap 2.x |
| Scheduling | APScheduler BlockingScheduler |
| Website & podcast | Jekyll on GitHub Pages |
| Social | Mastodon (optional) |

---

## Programme schedule

| Slot | Time | Vibe |
|------|------|------|
| Morning Drift | 06:00–09:00 | Gentle start, long reads, ideas |
| The Stack | 09:00–12:00 | Tech, science, Hacker News |
| Midday | 12:00–14:00 | World news, current affairs |
| Deep Cuts | 14:00–17:00 | Essays, philosophy, deep dives |
| Drive | 17:00–19:00 | Stories for the commute |
| Night School | 19:00–22:00 | Learning, history, culture |
| Archive | 22:00–06:00 | Overnight ambient mix |

---

## Deployment

### Oracle Cloud (recommended — free forever)

Oracle's Always Free tier gives you a VM.Standard.A1.Flex (Ampere ARM) with **4 OCPUs and 24 GB RAM** at no cost. Gemma 4 E4B (9 GB) fits comfortably with headroom for everything else.

See **[DEPLOY.md](DEPLOY.md)** for the full step-by-step guide.

### Google Cloud Platform

GCP's e2-standard-4 (4 vCPU / 16 GB) runs the same stack. Costs ~$100/month after the $300 free trial.

See **[DEPLOY_GCP.md](DEPLOY_GCP.md)** for the full step-by-step guide.

---

## Quick start (local test)

```bash
# Clone and set up
git clone https://github.com/clifford-smith/the-long-view.git
cd the-long-view
python3.11 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Pull the model (requires Ollama installed)
ollama pull gemma4:e4b

# Generate one segment to verify everything works
python main.py --generate morning_drift

# Run the full scheduler (blocks, generates content ahead of each slot)
python main.py --schedule
```

---

## Configuration

Edit `config.yml` before first run:

```yaml
station:
  stream_url: "http://YOUR_VM_IP:8000/stream"

llm:
  model: "gemma4:e4b"   # or gemma4:e2b for 8 GB VRAM GPUs

tts:
  voice: "en-US-AriaNeural"
```

The music library lives in `audio/assets/music/`. Add MP3s and rebuild the index with `audio/assets/music_index.json`.

---

## Monetisation

The station supports three passive revenue streams, all opt-in:

- **Ko-fi / Patreon** — links read out by Aria and displayed on the website
- **Affiliate links** — Bookshop, Audible, Brilliant woven naturally into relevant segments
- **Sponsor spots** — 30-second reads, scheduled per slot, with automatic ethical vetting

Sponsors are defined in `content/sponsors.yml`. Any sponsor tagged with a blocked category (anti-science, climate denial, fossil fuels, firearms, crypto, gambling, partisan politics, and others) is silently skipped regardless of their `active` flag.

---

## Tests

```bash
pytest -v
```

74 tests covering scheduling, content generation, TTS, assembly, RSS, sponsor vetting, affiliate injection, and distribution.

---

## Project structure

```
├── main.py                  # Entry point (--generate / --schedule)
├── config.yml               # All configuration
├── content/
│   ├── news_aggregator.py   # RSS feed fetching and dedup
│   ├── script_writer.py     # LLM script generation
│   ├── topic_researcher.py  # Topic selection per slot
│   ├── music_selector.py    # Mood-matched music selection
│   └── prompts/             # Per-slot system prompts for Aria
├── audio/
│   ├── tts_engine.py        # edge-tts rendering + FFmpeg concat
│   └── show_assembler.py    # Full segment assembly + loudnorm
├── stream/
│   └── scheduler.py         # APScheduler + startup validation
├── distribution/
│   ├── rss_generator.py     # Podcast feed (RSS 2.0)
│   ├── show_notes.py        # Jekyll blog post writer
│   └── social_poster.py     # Mastodon posting
├── monetization/
│   ├── sponsor_manager.py   # Sponsor vetting and slot matching
│   └── affiliate_injector.py
├── stream/
│   ├── icecast.xml          # Icecast2 configuration
│   └── liquidsoap.liq       # Liquidsoap stream automation
└── website/                 # GitHub Pages site + podcast feed
```

---

## Licence

MIT. Do what you like. If you build something with it, a mention would be appreciated.
