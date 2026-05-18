from __future__ import annotations
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)


@dataclass
class SegmentParts:
    intro_jingle: Path | None
    speech: Path
    music: Path | None
    outro_jingle: Path | None
    sponsor: Path | None = None


def build_segment_order(parts: SegmentParts) -> list[Path]:
    order: list[Path] = []
    if parts.intro_jingle:
        order.append(parts.intro_jingle)
    order.append(parts.speech)
    if parts.sponsor:
        order.append(parts.sponsor)
    if parts.music:
        order.append(parts.music)
    if parts.outro_jingle:
        order.append(parts.outro_jingle)
    return order


def assemble_segment(parts: SegmentParts, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_order = build_segment_order(parts)
    log.info("Assembling segment %s from %d files.", output_path.name, len(file_order))

    concat_list = output_path.parent / f"_{output_path.stem}_concat.txt"
    with open(concat_list, "w") as f:
        for path in file_order:
            f.write(f"file '{path.resolve()}'\n")

    try:
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar", "44100", "-b:a", "128k",
            str(output_path), "-y"
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        log.error("FFmpeg assembly failed for %s: %s", output_path.name, exc.stderr.decode(errors="replace"))
        raise

    concat_list.unlink(missing_ok=True)
    return output_path
