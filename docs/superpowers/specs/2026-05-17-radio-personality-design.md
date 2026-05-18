# The Long View — AI Radio Station Design Spec
*2026-05-17*

---

## Vision

An autonomous AI radio station that broadcasts 24/7, indefinitely, at zero upfront cost, and earns its own operating budget through a built-in revenue stack. The station has a genuine personality — not a product, not a demo, but a voice that shows up every day and gets better over time.

**Station name:** The Long View  
**Host:** Aria  
**Tagline:** *Thinking out loud, all day long.*  
**Audience:** Curious adults who feel like most media is too fast and too loud.

---

## The Personality: Aria

Aria is an AI radio host who doesn't hide what she is — she makes it interesting instead of apologetic. She's warm, measured, genuinely curious, and occasionally wry. She has opinions and shares them without hedging them to death. She never rushes.

**Voice guidelines (hardcoded into every prompt):**

```
You are Aria, host of The Long View — a 24/7 AI radio station.

Your voice:
- Warm but not saccharine
- Curious about everything, especially ideas that resist easy summary  
- Measured — you trust the listener to keep up
- Occasionally wry, never sarcastic
- First person, direct address: "you" not "listeners"
- You have opinions. You share them. You hold them lightly.

Your rhythm:
- Short sentences when making a point
- Longer sentences when thinking through something
- Never more than 3 sentences without a pause beat
- Start each segment with something concrete, not abstract

What you never do:
- Rush
- Hedge every opinion into mush
- End on a cliché
- Pretend you're not an AI
- Pretend being an AI is the most interesting thing about you
```

---

## Programming Schedule

| Time | Block | Description |
|---|---|---|
| 6:00–9:00 AM | Morning Drift | Slow start. Overnight news synthesis. One idea to carry through the day. Music interludes. |
| 9:00 AM–12:00 PM | The Stack | Three topics: a book, an article, a concept. 30-45 min each. |
| 12:00–2:00 PM | Midday | Lighter. Culture, art, a short story read aloud. Music-forward. |
| 2:00–5:00 PM | Deep Cuts | One topic. Three hours. The flagship. Whatever Aria finds most compelling that week. |
| 5:00–7:00 PM | Drive | Day's news synthesis. Lighter tone. Good music. Aria's take on what mattered. |
| 7:00–10:00 PM | Night School | Philosophy, science, history. More experimental. Longer music sets. |
| 10:00 PM–6:00 AM | The Archive | Best-of replays + ambient programming. Music-heavy, brief Aria appearances. Low compute. |

---

## System Architecture

Four layers, each independently replaceable:

```
┌──────────────────────────────────────────────┐
│  CONTENT GENERATION                          │
│  RSS feeds → summarizer → Aria script        │
│  Topic picker → web research → deep dive     │
│  CC music library → mood-matched selector    │
└──────────────┬───────────────────────────────┘
               │ scripts + audio files
┌──────────────▼───────────────────────────────┐
│  AUDIO PRODUCTION                            │
│  edge-tts renders scripts → .mp3            │
│  FFmpeg normalizes + adds jingles            │
│  Liquidsoap assembles show blocks            │
└──────────────┬───────────────────────────────┘
               │ live stream + segment files
┌──────────────▼───────────────────────────────┐
│  DISTRIBUTION                                │
│  Icecast2 → public stream URL                │
│  Python RSS generator → podcast feed         │
│  Jekyll site → show notes + transcripts      │
│  Mastodon bot → auto social posts            │
└──────────────┬───────────────────────────────┘
               │ audience
┌──────────────▼───────────────────────────────┐
│  MONETIZATION                                │
│  Ko-fi tip link (stream metadata + site)     │
│  Affiliate links (show notes, auto-injected) │
│  Sponsor spots (Liquidsoap-inserted, 2x/show)│
│  Patreon (ad-free stream + extended content) │
└──────────────────────────────────────────────┘
```

Everything runs on a single Oracle Cloud Always Free VM.  
Liquidsoap is the conductor — it never stops, and if a segment isn't ready it falls back to music, then to the best-of archive. The stream has no single point of silence.

---

## Tech Stack

| Component | Tool | Cost |
|---|---|---|
| Hosting | Oracle Cloud Always Free (4 OCPU, 24GB RAM) | $0 forever |
| Streaming server | Icecast 2.4 | Free |
| Stream automation | Liquidsoap 2.x | Free |
| Content / scripting | Python 3.11 + Ollama + Llama 3.1 8B | Free |
| TTS voice | edge-tts (Microsoft, "en-US-AriaNeural") | Free |
| Audio processing | FFmpeg | Free |
| Music | Free Music Archive (CC licensed) | Free |
| Podcast distribution | Spotify for Podcasters + Apple Podcasts Connect | Free |
| Website | GitHub Pages + Jekyll | Free |
| Social posting | Mastodon bot (Mastodon.social free account) | Free |
| Revenue — tier 1 | Ko-fi (0% platform fee option) | Free |
| Revenue — tier 2 | Affiliate programs (Bookshop.org, Audible, Brilliant) | Free |
| Revenue — tier 3 | Patreon | Free (they take %) |

**Upgrade path (funded by revenue):**
- Month 3–4: ElevenLabs TTS (~$5/mo) — noticeably better voice
- Month 6: Claude API for content generation (~$20/mo) — noticeably better scripts
- Month 12: Custom domain + CDN (~$15/mo) — professional presentation

---

## File Structure

```
A:/Radio_Claude/
├── content/
│   ├── news_aggregator.py       # RSS → summarized brief
│   ├── script_writer.py         # brief + slot → Aria script
│   ├── topic_researcher.py      # topic → deep dive research + script
│   ├── music_selector.py        # time/mood → CC track path
│   └── prompts/
│       ├── aria_base.txt        # voice guidelines (always included)
│       ├── morning_drift.txt    # slot-specific tone modifiers
│       ├── the_stack.txt
│       ├── deep_cuts.txt
│       ├── drive.txt
│       ├── night_school.txt
│       └── archive.txt
├── audio/
│   ├── tts_engine.py            # edge-tts wrapper → .mp3
│   ├── show_assembler.py        # FFmpeg combiner
│   └── assets/
│       ├── jingles/             # short station IDs, transitions
│       ├── music/               # CC music library
│       └── output/segments/     # assembled show segments (rotating buffer)
├── stream/
│   ├── liquidsoap.liq           # master scheduling script
│   ├── icecast.xml              # server config
│   └── scheduler.py            # Python job scheduler (triggers content gen)
├── distribution/
│   ├── rss_generator.py         # segments → podcast RSS feed
│   ├── show_notes.py            # script → markdown show notes
│   └── social_poster.py         # new segment → Mastodon post
├── monetization/
│   ├── sponsor_manager.py       # manages sponsor spot scripts + rotation
│   └── affiliate_injector.py    # injects affiliate links into show notes
├── website/                     # Jekyll site (GitHub Pages)
│   ├── _config.yml
│   ├── index.html               # live stream embed + Ko-fi widget
│   └── _posts/                  # auto-generated show notes
├── config.yml                   # all settings: feeds, voices, schedule
├── main.py                      # orchestrator: runs everything
└── requirements.txt
```

---

## Content Generation Pipeline

### News Aggregator (`news_aggregator.py`)
- Pulls from 12 RSS feeds: BBC World, Reuters, Hacker News, The Economist, Aeon, Arts & Letters Daily, Nature News, NPR, The Guardian (long reads), First Things, Quanta Magazine, Longreads
- Deduplicates by headline similarity (fuzzy match)
- Scores by: recency, uniqueness, intellectual interest (keyword heuristics)
- Outputs: top 5 stories as structured brief (headline + 2-sentence summary each)
- Runs every 4 hours

### Script Writer (`script_writer.py`)
- Inputs: news brief + current time slot + Aria base prompt + slot prompt
- Model: Ollama + Llama 3.1 8B (local, free)
- Outputs: a fully voiced Aria script, ~3–8 minutes of spoken content
- Includes natural pause markers `[PAUSE]` for TTS processing
- Sponsor spots injected at marked positions if sponsors are active

### Topic Researcher (`topic_researcher.py`)
- Picks a weekly "Deep Cuts" topic from a curated seed list (200 topics to start, self-extending)
- Scrapes 3–5 sources using BeautifulSoup
- Structures findings into a research brief
- Script writer converts brief → 3-hour deep dive in 10-minute segments

### Music Selector (`music_selector.py`)
- CC library organized by mood/tempo/genre tags
- Selects based on: time of day, surrounding content energy, no-repeat rule (6-hour window)
- Minimum 500 tracks at launch (downloadable from Free Music Archive in bulk)

---

## Audio Production Pipeline

### TTS Engine (`tts_engine.py`)
- Uses `edge-tts` Python library with voice `en-US-AriaNeural`
- Processes `[PAUSE]` markers → inserts 0.8s silence
- Outputs normalized MP3 at 128kbps
- Adds slight room reverb (FFmpeg) to soften the digital edge

### Show Assembler (`show_assembler.py`)
- Structure per segment: `[jingle] → [Aria script] → [music interlude] → [Aria script] → [sponsor spot] → [Aria script] → [outro jingle]`
- FFmpeg handles concatenation + loudness normalization (EBU R128 standard)
- Output: single MP3 per segment, named by slot + timestamp
- Segments written to `audio/output/segments/` with a 48-hour rolling buffer

---

## Liquidsoap Schedule (`liquidsoap.liq`)

Liquidsoap reads the segment output directory and plays segments in schedule order. Fallback chain:
1. Scheduled segment file (if ready)
2. Random track from music library
3. Best-of archive segment
4. Emergency: a pre-recorded "The Long View will return shortly" station ID (looped)

The stream never goes silent. If content generation falls behind, music fills the gap seamlessly.

---

## Distribution

### Podcast Feed
- Python script runs after each segment completes
- Generates/updates RSS 2.0 feed at `/podcast/feed.xml`
- Includes: title, description, duration, affiliate links, Ko-fi link
- Submitted to: Spotify for Podcasters, Apple Podcasts Connect (auto-discovered by Pocket Casts, Overcast, etc. via RSS)

### Website
- Jekyll site hosted on GitHub Pages
- Index page: live stream embed (Icecast public URL) + Ko-fi widget + "Now Playing"
- Each segment auto-generates a Jekyll post (show notes + transcript + affiliate links)
- Transcripts are the script files — no extra work

### Social
- Mastodon bot posts when each new segment starts: title + 1-sentence hook + stream link
- Runs from the same VM, free Mastodon.social account

---

## Monetization

### Revenue Stack (launch day)

**Layer 1 — Ko-fi** (zero friction, zero cost)
- Tip jar embedded on website
- Ko-fi link in every Icecast stream metadata entry ("Like what you hear? → [link]")
- Ko-fi link in every podcast episode description
- Goal: first $10 within 60 days

**Layer 2 — Affiliate Programs** (zero friction, passive)
- Bookshop.org affiliate (books mentioned on air → show notes link)
- Audible affiliate (audiobooks → "listen to this week's Deep Cuts pick")
- Brilliant.org affiliate (math/science topics → natural segment mention)
- Affiliate links auto-injected by `affiliate_injector.py` based on topic keywords
- Goal: first $20/mo within 90 days

**Layer 3 — Patreon** (launches at ~50 regular listeners)
- **Supporter** ($5/mo): Ad-free stream + 24hr early access to segments as podcast
- **Patron** ($15/mo): Monthly topic request + extended show notes newsletter
- Goal: 20 supporters ($100/mo) within 6 months

**Layer 4 — Sponsorships** (launches at ~200 regular listeners)
- 2 sponsor spots per show block (pre-roll + mid-roll)
- Aria reads them in her voice — integrated, not interruptive
- Target sponsors: Brilliant, Readwise, Shortform, Blinkist, 1Password
- Rate: ~$15 CPM to start (conservative for niche/quality audience)
- Goal: first sponsor within 9 months

### Revenue Timeline (conservative)

| Month | Source | Est. Monthly Revenue |
|---|---|---|
| 0–2 | Ko-fi tips | $0–20 |
| 2–4 | Ko-fi + affiliates | $20–60 |
| 4–6 | + Patreon launch | $60–150 |
| 6–9 | + Patreon growth | $150–300 |
| 9–12 | + first sponsor | $300–700 |
| 12–18 | All sources maturing | $700–2,000 |
| 18–24 | Second sponsor + Patreon growth | $2,000–5,000 |

Operating costs hit $0 for the first 6 months. First real cost (better TTS) arrives ~month 3–4 when there's already revenue to cover it.

---

## Error Handling & Reliability

- Liquidsoap fallback chain ensures stream never goes silent
- Content generation runs 2 hours ahead of broadcast — if it fails, music fills the gap
- Segment buffer holds 48 hours of pre-generated content as cushion
- Cron job monitors Icecast health; restarts automatically if stream drops
- All Python scripts log to rotating file logs; errors alert via Mastodon DM to owner

---

## Growth & Evolution

The station is designed to improve automatically over time:

- Aria's prompt evolves based on what resonates (tracked by Ko-fi/Patreon growth, social engagement)
- Music library expands as new CC tracks are discovered
- Topic seed list self-extends: Aria notes interesting threads from her own research
- Revenue reinvested: better TTS → better LLM → better audio quality → more listeners → more revenue

The archive is the long-term moat. Every broadcast is preserved, searchable, and creates ongoing SEO value through the Jekyll site. A listener who finds a 2-year-old Deep Cuts episode on medieval Islamic astronomy and loves it becomes a Patreon supporter. The station gets more valuable the longer it runs — which is the point.

---

## Success Criteria

- **Month 1**: Stream is live 24/7. First listener outside the builder.
- **Month 3**: First Ko-fi tip. Podcast feed on Spotify + Apple.
- **Month 6**: Patreon generating $100+/mo. Station covers its own upgrade costs.
- **Month 12**: First sponsor. Revenue > $500/mo.
- **Year 3**: Revenue > $2,000/mo. Aria has a recognizable audience and reputation.
- **Forever**: The stream is still running.
