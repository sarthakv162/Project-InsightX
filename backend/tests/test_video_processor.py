"""Tests for VideoProcessor.

Tests that don't require a real video file use a mock capture.
Tests that require OpenCV operations use a synthetic video.
"""

import cv2
import numpy as np
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


def _create_test_video(path: str, num_frames: int = 30, fps: float = 30.0):
    """Create a small synthetic video for testing."""
    width, height = 320, 240
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))

    for i in range(num_frames):
        # Create frames with slight movement for optical flow testing
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Moving circle — shifts right over frames
        cx = int(50 + i * 5) % width
        cy = height // 2
        cv2.circle(frame, (cx, cy), 20, (0, 255, 0), -1)
        writer.write(frame)

    writer.release()


class TestVideoProcessorMetadata:
    """Test metadata extraction."""

    def test_quick_metadata(self):
        from utils.video_processor import VideoProcessor

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name

        try:
            _create_test_video(path, num_frames=60, fps=30.0)
            meta = VideoProcessor.quick_metadata(path)

            assert meta["total_frames"] == 60
            assert meta["fps"] == pytest.approx(30.0, rel=0.1)
            assert meta["duration_seconds"] == pytest.approx(2.0, rel=0.1)
            assert meta["width"] == 320
            assert meta["height"] == 240
            assert meta["resolution"] == [320, 240]
        finally:
            Path(path).unlink(missing_ok=True)

    def test_get_metadata_instance(self):
        from utils.video_processor import VideoProcessor

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name

        try:
            _create_test_video(path)
            proc = VideoProcessor(path)
            meta = proc.get_metadata()
            proc.close()

            assert "duration_seconds" in meta
            assert "fps" in meta
            assert "file_path" in meta
        finally:
            Path(path).unlink(missing_ok=True)


class TestVideoProcessorFrames:
    """Test frame extraction."""

    def test_get_frame(self):
        from utils.video_processor import VideoProcessor

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name

        try:
            _create_test_video(path, num_frames=30)
            with VideoProcessor(path) as proc:
                frame = proc.get_frame(0)
                assert frame is not None
                assert frame.shape == (240, 320, 3)

                # Out of bounds
                assert proc.get_frame(-1) is None
                assert proc.get_frame(1000) is None
        finally:
            Path(path).unlink(missing_ok=True)

    def test_extract_frames_at_fps(self):
        from utils.video_processor import VideoProcessor

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name

        try:
            _create_test_video(path, num_frames=60, fps=30.0)
            with VideoProcessor(path) as proc:
                # At 2 fps from a 30fps video: should get ~4 frames from 2s
                frames = proc.extract_frames_at_fps(2)
                assert len(frames) >= 3
        finally:
            Path(path).unlink(missing_ok=True)


class TestVideoProcessorInvalidFile:
    def test_invalid_path_raises(self):
        from utils.video_processor import VideoProcessor

        with pytest.raises(ValueError, match="Cannot open video"):
            VideoProcessor("/nonexistent/video.mp4")


class TestModuleLevelFunctions:
    def test_extract_video_metadata(self):
        from utils.video_processor import extract_video_metadata

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            path = f.name

        try:
            _create_test_video(path)
            meta = extract_video_metadata(path)
            assert meta["total_frames"] > 0
        finally:
            Path(path).unlink(missing_ok=True)
