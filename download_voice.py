import urllib.request
import os

base = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium"
dest = "/home/ubuntu/the-long-view/audio/assets/tts_models"
os.makedirs(dest, exist_ok=True)

for fname in ["en_US-amy-medium.onnx", "en_US-amy-medium.onnx.json"]:
    url = f"{base}/{fname}"
    path = f"{dest}/{fname}"
    if os.path.exists(path):
        print(f"Already exists: {fname}")
        continue
    print(f"Downloading {fname} ...")
    urllib.request.urlretrieve(url, path)
    print(f"Saved to {path}")

print("Done.")
