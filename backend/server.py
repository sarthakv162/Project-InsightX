"""InsightX — FastAPI Web Server.

Exposes the multi-agent pipeline via REST endpoints so the
Next.js frontend can send videos and queries.

Video uploads are processed through VideoProcessor to extract
metadata (fps, duration, resolution) before analysis begins.
"""

import os
import uuid
import logging
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config.settings import settings
from utils.gemini_client import GeminiClient
from utils.video_processor import VideoProcessor, extract_video_metadata
from workflows.insightx_workflow import InsightXWorkflow

# ── logging ───────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-22s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("insightx.server")

# ── app setup ─────────────────────────────────────────────────────────────

app = FastAPI(title="InsightX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── storage ───────────────────────────────────────────────────────────────

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory session store: session_id → { video_sources, sport, ... }
sessions: dict = {}

# Shared Gemini client + workflow
api_key = settings.GEMINI_API_KEY
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set — add it to backend/.env")

gemini = GeminiClient(api_key=api_key, model_name=settings.GEMINI_MODEL)
workflow = InsightXWorkflow(gemini)

# Thread pool for running the blocking pipeline off the event loop
_executor = ThreadPoolExecutor(max_workers=4)


# ── request / response models ────────────────────────────────────────────

class YouTubeRequest(BaseModel):
    url: str
    sport: str = "unknown"


class CompareYouTubeRequest(BaseModel):
    url1: str
    url2: str
    sport: str = "unknown"


class QueryRequest(BaseModel):
    session_id: str
    query: str
    sport: Optional[str] = None


class VideoMetadataResponse(BaseModel):
    duration_seconds: float
    fps: float
    total_frames: int
    resolution: List[int]
    width: int
    height: int


class SessionResponse(BaseModel):
    session_id: str
    status: str = "ready"
    source_type: str = "unknown"
    filename: Optional[str] = None
    youtube_url: Optional[str] = None
    filename2: Optional[str] = None
    youtube_url2: Optional[str] = None
    is_comparison: bool = False
    video_metadata: Optional[VideoMetadataResponse] = None


class AnalysisResponse(BaseModel):
    response: str
    session_id: str
    key_events: list = []


# ── helpers ───────────────────────────────────────────────────────────────

def _extract_and_validate_video(file_path: str) -> Dict[str, Any]:
    """Extract video metadata using VideoProcessor and validate duration.

    Raises HTTPException if the video exceeds VIDEO_MAX_DURATION.
    """
    try:
        metadata = extract_video_metadata(file_path)
    except ValueError as e:
        raise HTTPException(400, f"Invalid video file: {e}")

    if metadata["duration_seconds"] > settings.VIDEO_MAX_DURATION:
        raise HTTPException(
            400,
            f"Video too long: {metadata['duration_seconds']:.0f}s "
            f"(max {settings.VIDEO_MAX_DURATION}s)",
        )

    logger.info(
        f"Video metadata: {metadata['duration_seconds']:.1f}s, "
        f"{metadata['fps']:.1f} fps, {metadata['width']}×{metadata['height']}, "
        f"{metadata['total_frames']} frames"
    )
    return metadata


# ── endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "model": settings.GEMINI_MODEL}


@app.post("/api/video/upload", response_model=SessionResponse)
async def upload_video(
    file: UploadFile = File(...),
    sport: str = Form("unknown"),
):
    """Upload a local video file for analysis."""
    session_id = str(uuid.uuid4())
    safe_name = f"{session_id}_{file.filename}"
    dest = UPLOAD_DIR / safe_name

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract video metadata via VideoProcessor
    metadata = _extract_and_validate_video(str(dest.resolve()))

    sessions[session_id] = {
        "video_sources": [str(dest.resolve())],
        "sport": sport,
        "source_type": "upload",
        "filename": safe_name,
        "video_metadata": metadata,
    }
    logger.info(f"Uploaded {file.filename} → session {session_id}")

    return SessionResponse(
        session_id=session_id,
        status="ready",
        source_type="upload",
        filename=safe_name,
        video_metadata=VideoMetadataResponse(**metadata),
    )


@app.post("/api/video/youtube", response_model=SessionResponse)
async def youtube_video(body: YouTubeRequest):
    """Register a YouTube URL for analysis."""
    if not GeminiClient.is_youtube_url(body.url):
        raise HTTPException(400, "Invalid YouTube URL")

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "video_sources": [body.url.strip()],
        "sport": body.sport,
        "source_type": "youtube",
        "youtube_url": body.url.strip(),
    }
    logger.info(f"YouTube session {session_id}: {body.url}")

    return SessionResponse(
        session_id=session_id,
        status="ready",
        source_type="youtube",
        youtube_url=body.url.strip(),
    )


@app.post("/api/analysis/query", response_model=AnalysisResponse)
async def run_analysis(body: QueryRequest):
    """Run the full multi-agent analysis pipeline."""
    session = sessions.get(body.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    sport = body.sport or session.get("sport", "unknown")

    initial_state = {
        "user_query": body.query,
        "video_sources": session["video_sources"],
        "sport": sport,
        "chat_history": [],
        "video_metadata": session.get("video_metadata"),
    }

    logger.info(f"Running pipeline for session {body.session_id}")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, workflow.run, initial_state)
    except Exception as e:
        logger.exception("Pipeline error")
        raise HTTPException(500, f"Analysis failed: {e}")

    response_text = result.get("final_response", "No response generated.")
    key_events = result.get("key_events", [])
    return AnalysisResponse(response=response_text, session_id=body.session_id, key_events=key_events)


@app.post("/api/video/youtube-compare", response_model=SessionResponse)
async def youtube_compare(body: CompareYouTubeRequest):
    """Register two YouTube URLs for comparison analysis."""
    if not GeminiClient.is_youtube_url(body.url1):
        raise HTTPException(400, "Invalid YouTube URL for Video 1")
    if not GeminiClient.is_youtube_url(body.url2):
        raise HTTPException(400, "Invalid YouTube URL for Video 2")

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "video_sources": [body.url1.strip(), body.url2.strip()],
        "sport": body.sport,
        "source_type": "youtube",
        "youtube_url": body.url1.strip(),
        "youtube_url2": body.url2.strip(),
        "is_comparison": True,
    }
    logger.info(f"Compare session {session_id}: {body.url1} vs {body.url2}")

    return SessionResponse(
        session_id=session_id,
        status="ready",
        source_type="youtube",
        youtube_url=body.url1.strip(),
        youtube_url2=body.url2.strip(),
        is_comparison=True,
    )


@app.post("/api/video/upload-compare", response_model=SessionResponse)
async def upload_compare(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    sport: str = Form("unknown"),
):
    """Upload two video files for comparison analysis."""
    session_id = str(uuid.uuid4())
    safe1 = f"{session_id}_1_{file1.filename}"
    safe2 = f"{session_id}_2_{file2.filename}"
    dest1 = UPLOAD_DIR / safe1
    dest2 = UPLOAD_DIR / safe2

    with open(dest1, "wb") as f:
        shutil.copyfileobj(file1.file, f)
    with open(dest2, "wb") as f:
        shutil.copyfileobj(file2.file, f)

    # Extract metadata for both videos
    meta1 = _extract_and_validate_video(str(dest1.resolve()))
    meta2 = _extract_and_validate_video(str(dest2.resolve()))

    sessions[session_id] = {
        "video_sources": [str(dest1.resolve()), str(dest2.resolve())],
        "sport": sport,
        "source_type": "upload",
        "filename": safe1,
        "filename2": safe2,
        "is_comparison": True,
        "video_metadata": meta1,
        "video_metadata_2": meta2,
    }
    logger.info(f"Compare upload {file1.filename} vs {file2.filename} → session {session_id}")

    return SessionResponse(
        session_id=session_id,
        status="ready",
        source_type="upload",
        filename=safe1,
        filename2=safe2,
        is_comparison=True,
        video_metadata=VideoMetadataResponse(**meta1),
    )


@app.get("/api/video/file/{filename}")
async def serve_video(filename: str):
    """Serve an uploaded video file."""
    path = UPLOAD_DIR / filename
    if not path.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(path, media_type="video/mp4")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Return session metadata."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return {
        "session_id": session_id,
        "sport": session.get("sport"),
        "source_type": session.get("source_type"),
        "youtube_url": session.get("youtube_url"),
        "youtube_url2": session.get("youtube_url2"),
        "filename": session.get("filename"),
        "filename2": session.get("filename2"),
        "is_comparison": session.get("is_comparison", False),
        "video_metadata": session.get("video_metadata"),
    }


@app.get("/api/video/metadata/{session_id}")
async def get_video_metadata(session_id: str):
    """Return video metadata (fps, duration, resolution) for a session."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    metadata = session.get("video_metadata")
    if not metadata:
        raise HTTPException(404, "No metadata available (YouTube videos don't have local metadata)")
    return VideoMetadataResponse(**metadata)


# ── run ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
