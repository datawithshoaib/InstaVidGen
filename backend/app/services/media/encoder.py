"""Encode a still frame into a browser-playable H.264 MP4 using bundled ffmpeg."""

import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

from app.core.errors import RenderError


@lru_cache
def ffmpeg_exe() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def build_filters(duration: float, fade_in: float, fade_out: float) -> str:
    filters = []
    if fade_in > 0:
        filters.append(f"fade=t=in:st=0:d={fade_in:.2f}")
    if fade_out > 0:
        filters.append(f"fade=t=out:st={max(0.0, duration - fade_out):.2f}:d={fade_out:.2f}")
    filters.append("format=yuv420p")
    return ",".join(filters)


def encode_still_video(
    frame: Image.Image,
    output: Path,
    *,
    duration: float,
    fade_in: float,
    fade_out: float,
    fps: int = 30,
) -> None:
    """Write `frame` as an MP4 (H.264, yuv420p, faststart) with optional fades."""
    if frame.width % 2 or frame.height % 2:  # yuv420p needs even dimensions
        frame = frame.crop((0, 0, frame.width - frame.width % 2, frame.height - frame.height % 2))

    with tempfile.TemporaryDirectory(prefix="instavidgen-") as tmp:
        still = Path(tmp) / "frame.png"
        frame.save(still, "PNG")
        cmd = [
            ffmpeg_exe(),
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-loop", "1",
            "-framerate", str(fps),
            "-i", str(still),
            "-t", f"{duration:.2f}",
            "-vf", build_filters(duration, fade_in, fade_out),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "stillimage",
            "-crf", "20",
            "-r", str(fps),
            "-movflags", "+faststart",
            str(output),
        ]  # fmt: skip
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if proc.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        output.unlink(missing_ok=True)
        detail = (proc.stderr or "").strip().splitlines()[-1:] or ["unknown error"]
        raise RenderError(f"Video encoding failed: {detail[0]}")
