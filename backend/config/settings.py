"""Configuration settings for InsightX"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    """Global settings"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Gemini Model
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_CONTEXT_WINDOW: int = 1_000_000  # 1M tokens
    
    # Video Processing
    VIDEO_MAX_DURATION: int = 900  # 15 minutes
    VIDEO_SAMPLE_FPS: int = 2  # Sample frames at 2 FPS for initial analysis
    VIDEO_BURST_FPS: int = 15  # High-speed burst at 15 FPS for critical moments
    FRAME_QUALITY: int = 85  # JPEG quality
    
    # Context Caching
    ENABLE_CONTEXT_CACHING: bool = True
    CACHE_TTL_MINUTES: int = 60  # Cache time-to-live
    
    # Agent Configuration
    AGENT_TIMEOUT: int = 120  # seconds
    MAX_RETRIES: int = 3
    
    # Sport-specific settings
    SPORT_SPECIFIC_PROMPTS: dict = {
        "cricket": {
            "key_metrics": ["bat angle", "foot position", "follow-through", "line and length"],
            "common_errors": ["playing across the line", "poor footwork", "weak follow-through"],
        },
        "tennis": {
            "key_metrics": ["grip", "footwork", "racquet angle", "timing"],
            "common_errors": ["late preparation", "poor court positioning", "incorrect spin"],
        },
        "basketball": {
            "key_metrics": ["stance", "hand position", "release angle", "follow-through"],
            "common_errors": ["traveling", "poor spacing", "defensive lapse"],
        },
    }
    
    # Thresholds
    CONFIDENCE_THRESHOLD: float = 0.6
    EVENT_DURATION_MIN_SECONDS: float = 0.5
    
    # Output Settings
    INCLUDE_FRAME_CAPTURES: bool = True
    INCLUDE_VISUAL_OVERLAYS: bool = True


settings = Settings()
