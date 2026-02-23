"""Video processing utilities using OpenCV"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video frame extraction and preprocessing"""
    
    def __init__(self, video_path: str):
        """Initialize video processor"""
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
        """Get video resolution"""
        return (self.width, self.height)
    
    def get_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """Get a specific frame by index"""
        if frame_index < 0 or frame_index >= self.total_frames:
            return None
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def get_frame_at_time(self, seconds: float) -> Optional[np.ndarray]:
        """Get frame at specific timestamp"""
        frame_index = int(seconds * self.fps)
        return self.get_frame(frame_index)
    
    def extract_frames_at_fps(self, target_fps: float) -> List[Tuple[int, np.ndarray]]:
        """Extract frames at target FPS"""
        frames = []
        frame_interval = int(self.fps / target_fps) if target_fps > 0 else 1
        
        frame_idx = 0
        while frame_idx < self.total_frames:
            frame = self.get_frame(frame_idx)
            if frame is not None:
                frames.append((frame_idx, frame))
            frame_idx += frame_interval
        
        return frames
    
    def extract_frame_burst(self, start_seconds: float, end_seconds: float, 
                           target_fps: float = 15) -> List[Tuple[float, np.ndarray]]:
        """Extract high-speed frame burst between timestamps"""
        start_frame = int(start_seconds * self.fps)
        end_frame = int(end_seconds * self.fps)
        frame_interval = int(self.fps / target_fps) if target_fps > 0 else 1
        
        frames = []
        for frame_idx in range(start_frame, min(end_frame, self.total_frames), frame_interval):
            frame = self.get_frame(frame_idx)
            if frame is not None:
                timestamp = frame_idx / self.fps
                frames.append((timestamp, frame))
        
        return frames
    
    def resize_frame(self, frame: np.ndarray, scale: float = 0.5) -> np.ndarray:
        """Resize frame by scale factor"""
        new_width = int(frame.shape[1] * scale)
        new_height = int(frame.shape[0] * scale)
        return cv2.resize(frame, (new_width, new_height))
    
    def compress_frame(self, frame: np.ndarray, quality: int = 85) -> bytes:
        """Compress frame to JPEG bytes"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return buffer.tobytes()
    
    def extract_roi(self, frame: np.ndarray, roi: Tuple[int, int, int, int]) -> np.ndarray:
        """Extract region of interest (x1, y1, x2, y2)"""
        x1, y1, x2, y2 = roi
        return frame[y1:y2, x1:x2]
    
    def get_optical_flow(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """Calculate optical flow between two frames"""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        return flow
    
    def detect_motion(self, frame1: np.ndarray, frame2: np.ndarray, 
                     threshold: float = 0.1) -> bool:
        """Detect if motion occurred between frames"""
        flow = self.get_optical_flow(frame1, frame2)
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        motion_ratio = np.sum(magnitude > 1) / magnitude.size
        return motion_ratio > threshold
    
    def close(self):
        """Release video resource"""
        if self.cap:
            self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def extract_video_summary(video_path: str, sample_fps: float = 2.0) -> Tuple[List[np.ndarray], dict]:
    """Extract summary frames from video"""
    processor = VideoProcessor(video_path)
    try:
        frames = processor.extract_frames_at_fps(sample_fps)
        metadata = {
            'duration': processor.duration_seconds,
            'fps': processor.fps,
            'resolution': processor.resolution,
            'total_frames': processor.total_frames,
        }
        return frames, metadata
    finally:
        processor.close()
