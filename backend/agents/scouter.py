"""Scouter Agent — Temporal Grounding & Event Detection.

Uses Gemini's native video understanding to find WHEN things happen.
Supports both local files and YouTube URLs transparently.

Post-processing:
  - Filters events below ``CONFIDENCE_THRESHOLD``
  - Drops events shorter than ``EVENT_DURATION_MIN_SECONDS``
"""

from agents.base_agent import BaseAgent
from utils.gemini_client import GeminiClient
from config.settings import settings
from typing import Dict, Any


class ScouterAgent(BaseAgent):
    """Find key events and timestamps using Gemini's native video understanding."""

    def __init__(self, gemini_client: GeminiClient):
        super().__init__("Scouter")
        self.gemini_client = gemini_client

    async def _execute_impl(self, state: Dict[str, Any]) -> Dict[str, Any]:
        video_sources = state.get("video_sources", [])
        if not video_sources:
            self.log("error", "No videos provided")
            return {}

        user_query = state.get("user_query", "")
        sport = state.get("sport", "unknown")

        self.log("info", f"Scouting video: {video_sources[0]}")

        # prepare_video handles both YouTube URLs and local files
        video_ref = self.gemini_client.prepare_video(video_sources[0])

        prompt = f"""
You are an expert {sport.upper()} video analyst performing temporal grounding.

User question: "{user_query}"

Watch the ENTIRE video carefully. Identify:
1. Every key moment — shots, serves, rallies, plays, movements, goals, faults
2. Critical turning points — errors, successes, momentum shifts
3. Moments specifically relevant to the user's question

For EACH event provide an exact timestamp (MM:SS format AND seconds).

Respond in JSON:
{{
  "events": [
    {{
      "event_type": "serve | volley | shot | goal | error | recovery | transition | other",
      "timestamp": "MM:SS",
      "start_seconds": 0.0,
      "end_seconds": 0.0,
      "confidence": 0.0,
      "description": "What happens and why it matters",
      "visual_cues": ["observable detail 1", "observable detail 2"]
    }}
  ],
  "summary": "One-paragraph overview of all events and their significance"
}}
"""

        result = self.gemini_client.query_video_json(video_ref, prompt)

        events = result.get("events", [])
        summary = result.get("summary", "")

        # ── Apply quality filters from settings ──────────────────
        raw_count = len(events)
        events = [
            e
            for e in events
            if e.get("confidence", 0) >= settings.CONFIDENCE_THRESHOLD
        ]
        events = [
            e
            for e in events
            if (e.get("end_seconds", 0) - e.get("start_seconds", 0))
            >= settings.EVENT_DURATION_MIN_SECONDS
        ]
        filtered = raw_count - len(events)
        if filtered:
            self.log(
                "info",
                f"Filtered {filtered}/{raw_count} events "
                f"(confidence < {settings.CONFIDENCE_THRESHOLD} "
                f"or duration < {settings.EVENT_DURATION_MIN_SECONDS}s)",
            )

        self.log("info", f"Detected {len(events)} events")

        return {
            "key_events": events,
            "scouter_summary": summary,
        }
