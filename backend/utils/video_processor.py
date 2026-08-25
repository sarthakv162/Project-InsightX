"""Video processing utilities using OpenCV.

Provides:
  - Frame extraction at configurable FPS
  - Quick metadata extraction (duration, fps, resolution)
  - Optical-flow-based action-segment detection for pre-filtering
  - Frame burst extraction for high-speed analysis windows
  - ROI cropping, compression, and resize helpers

Used by the upload endpoint to extract metadata and by the
workflow to optionally pre-filter action-heavy segments before
sending to Gemini — reducing API cost on long uploads.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import logging
import time

from config.settings import settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video frame extraction and preprocessing."""

    def __init__(self, video_path: str):
        """Initialize video processor.

        Args:
            video_path: Absolute path to the video file.

        Raises:
            ValueError: If the video cannot be opened by OpenCV.
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration_seconds = self.total_frames / self.fps if self.fps > 0 else 0

    @property
    def resolution(self) -> Tuple[int, int]:
        """Get video resolution as (width, height)."""
        return (self.width, self.height)

    # ── Quick metadata (no heavy processing) ──────────────────────

    def get_metadata(self) -> Dict[str, Any]:
        """Return lightweight metadata dict without reading frames.

        This is used by the upload endpoint to record video properties
        before any analysis begins.
        """
        return {
            "duration_seconds": round(self.duration_seconds, 2),
            "fps": round(self.fps, 2),
            "total_frames": self.total_frames,
            "resolution": list(self.resolution),
            "width": self.width,
            "height": self.height,
            "file_path": self.video_path,
        }

    @staticmethod
    def quick_metadata(video_path: str) -> Dict[str, Any]:
        """Extract metadata without keeping the processor alive."""
        proc = VideoProcessor(video_path)
        try:
            return proc.get_metadata()
        finally:
            proc.close()

    # ── Frame access ──────────────────────────────────────────────

    def get_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """Get a specific frame by index."""
        if frame_index < 0 or frame_index >= self.total_frames:
            return None

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.cap.read()
        return frame if ret else None

    def get_frame_at_time(self, seconds: float) -> Optional[np.ndarray]:
        """Get frame at specific timestamp."""
        frame_index = int(seconds * self.fps)
        return self.get_frame(frame_index)

    def extract_frames_at_fps(
        self, target_fps: float = None
    ) -> List[Tuple[int, np.ndarray]]:
        """Extract frames at target FPS (defaults to VIDEO_SAMPLE_FPS)."""
        target_fps = target_fps or settings.VIDEO_SAMPLE_FPS
        frames = []
        frame_interval = int(self.fps / target_fps) if target_fps > 0 else 1

        frame_idx = 0
        while frame_idx < self.total_frames:
            frame = self.get_frame(frame_idx)
            if frame is not None:
                frames.append((frame_idx, frame))
            frame_idx += frame_interval

        return frames

    def extract_frame_burst(
        self,
        start_seconds: float,
        end_seconds: float,
        target_fps: float = None,
    ) -> List[Tuple[float, np.ndarray]]:
        """Extract high-speed frame burst between timestamps.

        Uses VIDEO_BURST_FPS from settings as the default rate.
        """
        target_fps = target_fps or settings.VIDEO_BURST_FPS
        start_frame = int(start_seconds * self.fps)
        end_frame = int(end_seconds * self.fps)
        frame_interval = int(self.fps / target_fps) if target_fps > 0 else 1

        frames = []
        for frame_idx in range(
            start_frame, min(end_frame, self.total_frames), frame_interval
        ):
            frame = self.get_frame(frame_idx)
            if frame is not None:
                timestamp = frame_idx / self.fps
                frames.append((timestamp, frame))

        return frames

    # ── Action segment detection (optical flow) ───────────────────

    def find_action_segments(
        self,
        sample_fps: float = None,
        motion_threshold: float = 0.1,
        min_segment_seconds: float = None,
    ) -> List[Dict[str, Any]]:
        """Detect high-motion segments using optical flow.

        Samples frames at *sample_fps*, computes dense optical flow
        between consecutive samples, and groups contiguous high-motion
        windows into segments.

        This is the pre-filtering step that avoids sending 15 minutes
        of idle footage to the VLM — only the action-heavy windows
        are flagged for detailed analysis.

        Args:
            sample_fps: Sampling rate (defaults to VIDEO_SAMPLE_FPS).
            motion_threshold: Fraction of pixels that must exceed the
                flow-magnitude threshold to count as "motion".
            min_segment_seconds: Minimum segment duration to report
                (defaults to EVENT_DURATION_MIN_SECONDS).

        Returns:
            List of dicts with keys: start_seconds, end_seconds,
            duration_seconds, avg_motion_score.
        """
        sample_fps = sample_fps or settings.VIDEO_SAMPLE_FPS
        min_segment_seconds = (
            min_segment_seconds
            if min_segment_seconds is not None
            else settings.EVENT_DURATION_MIN_SECONDS
        )

        t0 = time.time()
        frames = self.extract_frames_at_fps(sample_fps)
        if len(frames) < 2:
            return []

        # Compute per-gap motion scores
        motion_scores: List[Tuple[float, float]] = []  # (timestamp, score)
        interval = 1.0 / sample_fps

        for i in range(len(frames) - 1):
            idx_a, frame_a = frames[i]
            idx_b, frame_b = frames[i + 1]

            gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY)
            gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(
                gray_a, gray_b, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
            score = float(np.sum(magnitude > 1) / magnitude.size)
            ts = idx_a / self.fps
            motion_scores.append((ts, score))

        # Group contiguous above-threshold windows
        segments: List[Dict[str, Any]] = []
        seg_start = None
        seg_scores: List[float] = []

        for ts, score in motion_scores:
            if score >= motion_threshold:
                if seg_start is None:
                    seg_start = ts
                seg_scores.append(score)
            else:
                if seg_start is not None:
                    seg_end = ts + interval
                    duration = seg_end - seg_start
                    if duration >= min_segment_seconds:
                        segments.append(
                            {
                                "start_seconds": round(seg_start, 2),
                                "end_seconds": round(seg_end, 2),
                                "duration_seconds": round(duration, 2),
                                "avg_motion_score": round(
                                    float(np.mean(seg_scores)), 4
                                ),
                            }
                        )
                    seg_start = None
                    seg_scores = []

        # Close trailing segment
        if seg_start is not None:
            seg_end = motion_scores[-1][0] + interval
            duration = seg_end - seg_start
            if duration >= min_segment_seconds:
                segments.append(
                    {
                        "start_seconds": round(seg_start, 2),
                        "end_seconds": round(seg_end, 2),
                        "duration_seconds": round(duration, 2),
                        "avg_motion_score": round(
                            float(np.mean(seg_scores)), 4
                        ),
                    }
                )

        elapsed = time.time() - t0
        logger.info(
            f"Action detection: {len(segments)} segments found in "
            f"{elapsed:.1f}s (sampled {len(frames)} frames at {sample_fps} fps)"
        )
        return segments

    # ── Helpers ────────────────────────────────────────────────────

    def resize_frame(self, frame: np.ndarray, scale: float = 0.5) -> np.ndarray:
        """Resize frame by scale factor."""
        new_width = int(frame.shape[1] * scale)
        new_height = int(frame.shape[0] * scale)
        return cv2.resize(frame, (new_width, new_height))

    def compress_frame(self, frame: np.ndarray, quality: int = None) -> bytes:
        """Compress frame to JPEG bytes (uses FRAME_QUALITY from settings)."""
        quality = quality or settings.FRAME_QUALITY
        _, buffer = cv2.imencode(
            ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality]
        )
        return buffer.tobytes()

    def extract_roi(
        self, frame: np.ndarray, roi: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """Extract region of interest (x1, y1, x2, y2)."""
        x1, y1, x2, y2 = roi
        return frame[y1:y2, x1:x2]

    def get_optical_flow(
        self, frame1: np.ndarray, frame2: np.ndarray
    ) -> np.ndarray:
        """Calculate optical flow between two frames."""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        return flow

    def detect_motion(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        threshold: float = 0.1,
    ) -> bool:
        """Detect if motion occurred between frames."""
        flow = self.get_optical_flow(frame1, frame2)
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        motion_ratio = np.sum(magnitude > 1) / magnitude.size
        return motion_ratio > threshold

    # ── Resource management ───────────────────────────────────────

    def close(self):
        """Release video resource."""
        if self.cap:
            self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ── Module-level convenience functions ────────────────────────────

def extract_video_metadata(video_path: str) -> Dict[str, Any]:
    """Extract metadata from a video file without heavy processing."""
    return VideoProcessor.quick_metadata(video_path)


def extract_video_summary(
    video_path: str, sample_fps: float = None
) -> Tuple[List[np.ndarray], dict]:
    """Extract summary frames from video."""
    sample_fps = sample_fps or settings.VIDEO_SAMPLE_FPS
    processor = VideoProcessor(video_path)
    try:
        frames = processor.extract_frames_at_fps(sample_fps)
        metadata = processor.get_metadata()
        return frames, metadata
    finally:
        processor.close()


def detect_action_segments(
    video_path: str, sample_fps: float = None
) -> List[Dict[str, Any]]:
    """Detect high-motion action segments in a video.

    Convenience wrapper around VideoProcessor.find_action_segments().
    """
    sample_fps = sample_fps or settings.VIDEO_SAMPLE_FPS
    processor = VideoProcessor(video_path)
    try:
        return processor.find_action_segments(sample_fps=sample_fps)
    finally:
        processor.close()
