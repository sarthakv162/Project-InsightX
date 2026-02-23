"""YouTube video downloader (fallback for when direct URL mode fails).

Primary path: Gemini's new SDK supports YouTube URLs natively — no download
needed. This module is kept as a fallback for edge cases (e.g. private videos,
API quota limits, or when you need a local copy for OpenCV processing).
"""

import re
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

YOUTUBE_URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)"
    r"[\w\-]+"
)


def is_youtube_url(url: str) -> bool:
    """Return True if the string looks like a YouTube URL."""
    return bool(YOUTUBE_URL_PATTERN.search(url))


def download_youtube_video(
    url: str,
    output_dir: str = None,
    max_height: int = 720,
) -> str:
    """
    Download a YouTube video and return the local file path.

    Uses a single-stream format so ffmpeg is NOT required.
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp is required — pip install yt-dlp")

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="insightx_")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(title).50s.%(ext)s")

    ydl_opts = {
        # Single pre-muxed stream — NO ffmpeg merge needed
        "format": f"best[height<={max_height}][ext=mp4]/best[height<={max_height}]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    logger.info(f"Downloading YouTube video: {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        final_path = Path(filename)

    if not final_path.exists():
        raise FileNotFoundError(f"Download succeeded but file not found: {final_path}")

    logger.info(f"Downloaded to: {final_path}")
    return str(final_path)
