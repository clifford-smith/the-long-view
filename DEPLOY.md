# The Long View — Oracle Cloud Deployment Guide

Everything below runs on the Oracle Cloud VM, not your local machine. SSH in first.

---

## Step 1: Provision Oracle Cloud Always Free VM

1. Sign into [cloud.oracle.com](https://cloud.oracle.com)
2. Compute → Instances → Create Instance
3. Shape: **VM.Standard.A1.Flex** (Ampere) — 4 OCPUs, 24 GB RAM
4. OS: **Ubuntu 22.04** (Canonical)
5. Add your SSH public key (`~/.ssh/id_rsa.pub` or equivalent)
6. Create — note the public IP

SSH in:
```bash
ssh ubuntu@YOUR_ORACLE_IP
```

---

## Step 2: Install system dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip ffmpeg git curl
```

### Install Icecast2

```bash
sudo apt install -y icecast2
```

When the installer prompts for passwords, use the values you'll put in `stream/icecast.xml`.

### Install Liquidsoap

```bash
sudo apt install -y liquidsoap
```

Or install from OPAM for the latest version:
```bash
sudo apt install -y opam
opam init -a
opam install liquidsoap
```

---

## Step 3: Install Ollama and pull the model

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
```

This will take a few minutes. The model is ~4.7 GB.

Verify:
```bash
ollama run llama3.1:8b "Say hello as Aria."
```

---

## Step 4: Clone the repo and set up Python environment

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/the-long-view.git /home/ubuntu/the-long-view
cd /home/ubuntu/the-long-view
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 5: Fill in real values in config.yml

Edit `config.yml` and replace all placeholder values:

```bash
nano config.yml
```

Replace:
- `YOUR_ORACLE_IP` → your VM's public IP
- `YOUR_GITHUB_USERNAME` → your GitHub username

---

## Step 6: Configure Icecast

Replace the placeholder passwords in `stream/icecast.xml`, then install:

```bash
sudo cp stream/icecast.xml /etc/icecast2/icecast.xml
sudo systemctl enable icecast2
sudo systemctl start icecast2
```

Verify:
```bash
curl http://localhost:8000/status.xsl
```

---

## Step 7: Download CC music library (500+ tracks)

```bash
pip install yt-dlp
mkdir -p audio/assets/music

# Download ambient/instrumental tracks from Free Music Archive
# Search freemusicarchive.org for CC-licensed tracks and download:
yt-dlp --extract-audio --audio-format mp3 --audio-quality 5 \
  -o "audio/assets/music/%(title)s.%(ext)s" \
  "https://freemusicarchive.org/genre/Ambient/"

# Repeat for other genres as needed (Jazz, Classical, Electronic)
```

After downloading, rebuild the music index:

```bash
source venv/bin/activate
python - <<'EOF'
import json
from pathlib import Path

music_dir = Path("audio/assets/music")
tracks = []
for mp3 in music_dir.glob("*.mp3"):
    tracks.append({
        "path": str(mp3),
        "mood": "calm",       # Tag manually or extend this script
        "tempo": "slow",
        "genre": "ambient",
        "duration": 180,
        "title": mp3.stem,
    })

index = {"tracks": tracks, "recently_played": []}
Path("audio/assets/music_index.json").write_text(json.dumps(index, indent=2))
print(f"Indexed {len(tracks)} tracks.")
EOF
```

---

## Step 8: Generate the first segment manually

```bash
source venv/bin/activate
python main.py --generate morning_drift
```

Expected: logs show content generation → TTS render → assembly → show notes written.
A `.mp3` file appears in `audio/assets/output/segments/`.

---

## Step 9: Create station ID jingle (required for Liquidsoap fallback)

Record or generate a short (~10 second) station ID MP3 and save it:

```bash
# Quick option using edge-tts:
source venv/bin/activate
python - <<'EOF'
import asyncio, edge_tts
async def make_id():
    tts = edge_tts.Communicate("The Long View. Thinking out loud, all day long.", "en-US-AriaNeural")
    await tts.save("audio/assets/jingles/station_id.mp3")
asyncio.run(make_id())
EOF
```

---

## Step 10: Update Liquidsoap config

Edit `stream/liquidsoap.liq` and replace:
- `YOUR_KOFI_URL` → your Ko-fi URL
- `YOUR_WEBSITE_URL` → your GitHub Pages URL
- `CHANGE_THIS_SOURCE_PASSWORD` → same password as in `icecast.xml`

---

## Step 11: Create systemd services

### Liquidsoap stream service

```bash
sudo tee /etc/systemd/system/longview-stream.service > /dev/null <<'EOF'
[Unit]
Description=The Long View — Liquidsoap stream
After=icecast2.service
Requires=icecast2.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/the-long-view
ExecStart=/usr/bin/liquidsoap stream/liquidsoap.liq
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### Content scheduler service

```bash
sudo tee /etc/systemd/system/longview-scheduler.service > /dev/null <<'EOF'
[Unit]
Description=The Long View — Content Scheduler
After=network.target ollama.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/the-long-view
ExecStart=/home/ubuntu/the-long-view/venv/bin/python main.py --schedule
Restart=always
RestartSec=30
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable longview-stream longview-scheduler
sudo systemctl start longview-stream longview-scheduler
```

Check status:

```bash
sudo systemctl status longview-stream longview-scheduler
journalctl -u longview-scheduler -f
```

---

## Step 12: Open firewall port 8000

**On Oracle Cloud console:**
1. Networking → Virtual Cloud Networks → your VCN
2. Security Lists → Default Security List
3. Add Ingress Rule: Source `0.0.0.0/0`, Protocol TCP, Port `8000`

**On the VM:**

```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

**Test from your local machine:**
```
http://YOUR_ORACLE_IP:8000/stream
```

Open in VLC or a browser — Aria should be on air.

---

## Step 13: Deploy website to GitHub Pages

Create a GitHub repo named `the-long-view`. Then:

```bash
# On your local machine (not the VM)
cd /path/to/local/the-long-view
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/the-long-view.git
git push -u origin master

# Push the website folder to gh-pages branch
git subtree push --prefix website origin gh-pages
```

Go to GitHub repo → Settings → Pages → Source: `gh-pages` branch.

Update `website/index.html` and `website/_config.yml` with real URLs and push again.

---

## Step 14: Submit podcast to directories

Your podcast feed URL is:
```
https://YOUR_GITHUB_USERNAME.github.io/the-long-view/podcast/feed.xml
```

Submit to:
- **Spotify**: [podcasters.spotify.com](https://podcasters.spotify.com) → Add Podcast → paste feed URL
- **Apple Podcasts**: [podcastsconnect.apple.com](https://podcastsconnect.apple.com) → Add Show → paste feed URL

Both are free and take 24–72 hours to approve.

---

## Step 15: Set up Ko-fi

1. Create account at [ko-fi.com](https://ko-fi.com)
2. Copy your Ko-fi URL (e.g. `https://ko-fi.com/thelongview`)
3. Update `config.yml`: `monetization.kofi_url: "https://ko-fi.com/thelongview"`
4. Update `stream/liquidsoap.liq`: replace `YOUR_KOFI_URL`
5. Update `website/index.html`: replace `YOUR_KOFI_URL`
6. `git push` to redeploy

---

## Step 16: Set up Mastodon posting (optional)

1. Create an account on [mastodon.social](https://mastodon.social)
2. Go to Preferences → Development → New Application → give it "write:statuses" scope
3. Copy the access token
4. Add to `config.yml`:

```yaml
mastodon:
  access_token: "YOUR_ACCESS_TOKEN"
  instance: "https://mastodon.social"
```

---

## Monitoring

```bash
# Watch scheduler logs
journalctl -u longview-scheduler -f

# Watch stream logs
journalctl -u longview-stream -f

# Check Icecast listener count
curl -s http://localhost:8000/status-json.xsl | python3 -m json.tool

# Disk usage (segments accumulate)
du -sh audio/assets/output/
```

The `.gitignore` excludes MP3 files from the segments directory. Run a cron job to prune old segments:

```bash
# Delete segments older than 48 hours (add to crontab)
0 * * * * find /home/ubuntu/the-long-view/audio/assets/output/segments -name "*.mp3" -mmin +2880 -delete
```

Add to crontab:
```bash
crontab -e
# Add: 0 * * * * find /home/ubuntu/the-long-view/audio/assets/output/segments -name "*.mp3" -mmin +2880 -delete
```

---

## The station is live. Aria is on air.

From here, the system runs itself. The scheduler generates content 2 hours ahead of each slot. Liquidsoap plays it. The podcast feed updates automatically. Revenue grows as the audience does.

The only ongoing maintenance: keep the VM running, top up the music library occasionally, and activate sponsors in `content/sponsors.yml` when they arrive.
