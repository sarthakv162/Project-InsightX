"""Configuration settings for InsightX."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    """Global settings — every value here is read by at least one module.

    API Keys & Model
        GEMINI_API_KEY          — required; used by server.py, main.py, workflow
        GEMINI_MODEL            — model name passed to GeminiClient
        GEMINI_CONTEXT_WINDOW   — informational; max token budget

    Video Processing  (used by VideoProcessor & upload endpoint)
        VIDEO_MAX_DURATION      — reject uploads longer than this (seconds)
        VIDEO_SAMPLE_FPS        — frame sampling rate for action detection
        VIDEO_BURST_FPS         — high-speed burst rate for critical moments
        FRAME_QUALITY           — JPEG quality when compressing frames

    Context Caching  (used by GeminiClient)
        ENABLE_CONTEXT_CACHING  — cache uploaded video across agent calls
        CACHE_TTL_MINUTES       — cache time-to-live in minutes

    Agent Behaviour  (used by BaseAgent)
        AGENT_TIMEOUT           — per-agent timeout in seconds
        MAX_RETRIES             — retry count on timeout / error

    Sport-specific Prompts  (used by AnalystAgent)
        SPORT_SPECIFIC_PROMPTS  — per-sport key metrics and common errors
                                  injected into the analyst prompt

    Thresholds  (used by ScouterAgent & AnalystAgent)
        CONFIDENCE_THRESHOLD        — drop results below this confidence
        EVENT_DURATION_MIN_SECONDS  — drop events shorter than this

    Output Settings
        INCLUDE_FRAME_CAPTURES  — include frame captures in response
        INCLUDE_VISUAL_OVERLAYS — include visual overlays in response
    """

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
            "key_metrics": [
                "bat angle",
                "foot position",
                "follow-through",
                "line and length",
            ],
            "common_errors": [
                "playing across the line",
                "poor footwork",
                "weak follow-through",
            ],
        },
        "tennis": {
            "key_metrics": ["grip", "footwork", "racquet angle", "timing"],
            "common_errors": [
                "late preparation",
                "poor court positioning",
                "incorrect spin",
            ],
        },
        "basketball": {
            "key_metrics": [
                "stance",
                "hand position",
                "release angle",
                "follow-through",
            ],
            "common_errors": [
                "traveling",
                "poor spacing",
                "defensive lapse",
            ],
        },
        "football": {
            "key_metrics": [
                "body posture",
                "striking technique",
                "run timing",
                "passing accuracy",
            ],
            "common_errors": [
                "poor first touch",
                "wrong foot planted",
                "head down during play",
            ],
        },
        "badminton": {
            "key_metrics": [
                "grip switch speed",
                "lunge depth",
                "racquet preparation",
                "recovery step",
            ],
            "common_errors": [
                "flat-footed stance",
                "late racquet lift",
                "off-centre hitting",
            ],
        },
    }

    # Thresholds
    CONFIDENCE_THRESHOLD: float = 0.6
    EVENT_DURATION_MIN_SECONDS: float = 0.5

    # Output Settings
    INCLUDE_FRAME_CAPTURES: bool = True
    INCLUDE_VISUAL_OVERLAYS: bool = True


settings = Settings()
