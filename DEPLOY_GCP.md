# The Long View — Google Cloud Deployment Guide

Everything below runs on your GCP VM, not your local machine. SSH in first.

> **Cost note:** GCP's Always Free tier (e2-micro, 1 vCPU / 1 GB) is too small to run Ollama + Icecast.
> Use the **$300 free trial** (90 days) to get started, then budget ~$100/month for an e2-standard-4.
> Oracle Cloud Always Free (VM.Standard.A1.Flex, 4 OCPUs / 24 GB) is $0 forever — see `DEPLOY.md` if cost is a constraint.

---

## Step 1: Install the gcloud CLI (local machine)

Follow the official installer for your OS:
- **Windows / macOS / Linux:** https://cloud.google.com/sdk/docs/install

After installing:

```bash
gcloud init
```

Sign in with your Google account, select or create a project (e.g. `the-long-view`), and set a default region:

```bash
gcloud config set project the-long-view
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

Enable the Compute Engine API:

```bash
gcloud services enable compute.googleapis.com
```

---

## Step 2: Create the VM

```bash
gcloud compute instances create longview-radio \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --tags=longview-radio \
  --metadata=enable-oslogin=TRUE
```

**Shape breakdown:**
- `e2-standard-4` — 4 vCPU, 16 GB RAM (~$100/mo after free trial)
- 50 GB disk — enough for the model, music library, and 48 h of segments

Note the external IP in the output (`EXTERNAL_IP`).

SSH in:

```bash
gcloud compute ssh ubuntu@longview-radio --zone=us-central1-a
```

Or use standard SSH after adding your key:

```bash
ssh ubuntu@YOUR_EXTERNAL_IP
```

---

## Step 3: Open firewall port 8000

```bash
gcloud compute firewall-rules create allow-icecast \
  --allow=tcp:8000 \
  --target-tags=longview-radio \
  --description="Icecast streaming port" \
  --source-ranges=0.0.0.0/0
```

Verify the rule exists:

```bash
gcloud compute firewall-rules describe allow-icecast
```

---

## Step 4: Install system dependencies

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

## Step 5: Install Ollama and pull the model

```bash
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
ollama pull gemma4:e4b
```

This will take several minutes. The model is ~9 GB.

Verify:
```bash
ollama run gemma4:e4b "Say hello as Aria."
```

Gemma 4 model memory usage at Q8 quantization:

| Tag | Memory | Notes |
|-----|--------|-------|
| `gemma4:e2b` | 5.95 GB | Fits entirely in 8 GB VRAM (e.g. RTX 3060 Ti) with no CPU offload; fits any CPU-only VM |
| `gemma4:e4b` | 9.02 GB | **Default (this config)**; fits CPU-only VMs with ≥16 GB RAM |
| `gemma4:26b` | 17.99 GB | Oracle 24 GB only |
| `gemma4:31b` | 19.98 GB | Oracle 24 GB only (tight) |

> **On e2-standard-4 (16 GB):** `gemma4:e4b` (9.02 GB) fits with ~7 GB headroom for OS + services.
> Avoid `gemma4:26b` (17.99 GB) on GCP 16 GB VMs — use it only on Oracle's 24 GB instance.

---

## Step 6: Clone the repo and set up Python environment

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/the-long-view.git /home/ubuntu/the-long-view
cd /home/ubuntu/the-long-view
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 7: Fill in real values in config.yml

```bash
nano config.yml
```

Replace:
- `YOUR_ORACLE_IP` → your VM's external IP (GCP calls it `EXTERNAL_IP`)
- `YOUR_GITHUB_USERNAME` → your GitHub username

---

## Step 8: Configure Icecast

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

## Step 9: Download CC music library (500+ tracks)

```bash
pip install yt-dlp
mkdir -p audio/assets/music

# Download ambient/instrumental tracks from Free Music Archive
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
        "mood": "calm",
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

## Step 10: Generate the first segment manually

```bash
source venv/bin/activate
python main.py --generate morning_drift
```

Expected: logs show content generation → TTS render → assembly → show notes written.
A `.mp3` file appears in `audio/assets/output/segments/`.

---

## Step 11: Create station ID jingle (required for Liquidsoap fallback)

```bash
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

## Step 12: Update Liquidsoap config

Edit `stream/liquidsoap.liq` and replace:
- `YOUR_KOFI_URL` → your Ko-fi URL
- `YOUR_WEBSITE_URL` → your GitHub Pages URL
- `CHANGE_THIS_SOURCE_PASSWORD` → same password as in `icecast.xml`

---

## Step 13: Create systemd services

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

## Step 14: Test the stream

From your local machine, open in VLC or a browser:

```
http://YOUR_EXTERNAL_IP:8000/stream
```

Aria should be on air.

---

## Step 15: Deploy website to GitHub Pages

```bash
# On your local machine (not the VM)
cd /path/to/local/the-long-view
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/the-long-view.git
git push -u origin main

# Push the website folder to gh-pages branch
git subtree push --prefix website origin gh-pages
```

Go to GitHub repo → Settings → Pages → Source: `gh-pages` branch.

Update `website/index.html` and `website/_config.yml` with your real stream URL and push again.

---

## Step 16: Submit podcast to directories

Your podcast feed URL is:
```
https://YOUR_GITHUB_USERNAME.github.io/the-long-view/podcast/feed.xml
```

Submit to:
- **Spotify**: [podcasters.spotify.com](https://podcasters.spotify.com) → Add Podcast → paste feed URL
- **Apple Podcasts**: [podcastsconnect.apple.com](https://podcastsconnect.apple.com) → Add Show → paste feed URL

Both are free and take 24–72 hours to approve.

---

## Step 17: Set up Ko-fi

1. Create account at [ko-fi.com](https://ko-fi.com)
2. Copy your Ko-fi URL (e.g. `https://ko-fi.com/thelongview`)
3. Update `config.yml`: `monetization.kofi_url: "https://ko-fi.com/thelongview"`
4. Update `stream/liquidsoap.liq`: replace `YOUR_KOFI_URL`
5. Update `website/index.html`: replace `YOUR_KOFI_URL`
6. `git push` to redeploy

---

## Step 18: Set up Mastodon posting (optional)

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

Prune old segments with a cron job:

```bash
crontab -e
# Add: 0 * * * * find /home/ubuntu/the-long-view/audio/assets/output/segments -name "*.mp3" -mmin +2880 -delete
```

---

## Keeping costs down on GCP

The $300 free trial lasts 90 days. Once it runs out:

| Option | Cost | Trade-off |
|--------|------|-----------|
| `e2-standard-4` (4 vCPU / 16 GB) | ~$100/mo | Comfortable headroom for Ollama |
| `e2-standard-2` (2 vCPU / 8 GB) | ~$50/mo | Tight but workable; Ollama generation slower |
| `e2-medium` (2 vCPU / 4 GB) | ~$27/mo | Ollama may OOM under load |
| Oracle Cloud Always Free | $0/forever | 4 OCPUs / 24 GB Ampere — see `DEPLOY.md` |

To stop the VM without deleting it (saves ~95% cost while idle):

```bash
gcloud compute instances stop longview-radio --zone=us-central1-a
```

To restart:

```bash
gcloud compute instances start longview-radio --zone=us-central1-a
```

Note: the external IP changes on restart unless you reserve a static IP:

```bash
gcloud compute addresses create longview-ip --region=us-central1
gcloud compute instances delete-access-config longview-radio \
  --access-config-name="External NAT" --zone=us-central1-a
gcloud compute instances add-access-config longview-radio \
  --access-config-name="External NAT" \
  --address=$(gcloud compute addresses describe longview-ip \
              --region=us-central1 --format='get(address)') \
  --zone=us-central1-a
```

Static IPs cost ~$7/mo when not attached to a running instance; $0 when attached.

---

## The station is live. Aria is on air.

From here, the system runs itself. The scheduler generates content 2 hours ahead of each slot. Liquidsoap plays it. The podcast feed updates automatically.

The only ongoing maintenance: keep the VM running, top up the music library occasionally, and activate sponsors in `content/sponsors.yml` when they arrive.

**Adding sponsors:** Every sponsor entry requires a `categories` list. Sponsors whose categories match the blocked list in `monetization/sponsor_manager.py` are silently skipped at broadcast time regardless of their `active` flag. See `DEPLOY.md` for the full blocked categories list and an example entry.
