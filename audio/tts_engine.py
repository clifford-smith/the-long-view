from __future__ import annotations
import asyncio
import subprocess
from pathlib import Path
import edge_tts


def split_on_pauses(script: str) -> list[str]:
    return [p.strip() for p in script.split("[PAUSE]") if p.strip()]


async def _synthesize(text: str, voice: str, output_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


def _tts_part(text: str, voice: str, output_path: Path) -> Path:
    asyncio.run(_synthesize(text, voice, output_path))
    return output_path


def _concat_with_silence(part_files: list[Path], output_path: Path, silence_duration: float = 0.8) -> Path:
    tmp = output_path.parent / "_tts_work"
    tmp.mkdir(exist_ok=True)

    silence = tmp / "silence.mp3"
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", str(silence_duration), "-q:a", "9", "-acodec", "libmp3lame",
        str(silence), "-y"
    ], check=True, capture_output=True)

    concat_list = tmp / "concat.txt"
    with open(concat_list, "w") as f:
        for i, part in enumerate(part_files):
            f.write(f"file '{part.resolve()}'\n")
            if i < len(part_files) - 1:
                f.write(f"file '{silence.resolve()}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aecho=0.8:0.9:40:0.3",
        "-ar", "44100", "-b:a", "128k",
        str(output_path), "-y"
    ], check=True, capture_output=True)

    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()

    return output_path


def render_script(script: str, output_path: Path, voice: str = "en-US-AriaNeural") -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    parts = split_on_pauses(script)
    work_dir = output_path.parent / "_parts"
    work_dir.mkdir(exist_ok=True)

    part_files: list[Path] = []
    for i, text in enumerate(parts):
        part_path = work_dir / f"part_{i:03d}.mp3"
        _tts_part(text, voice, part_path)
        part_files.append(part_path)

    result = _concat_with_silence(part_files, output_path)

    for f in part_files:
        f.unlink(missing_ok=True)
    if work_dir.exists():
        try:
            work_dir.rmdir()
        except OSError:
            pass

    return result
