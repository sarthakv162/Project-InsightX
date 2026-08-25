"""Analyst Agent — Biomechanical & Kinematic Analysis.

Sends video(s) to Gemini for spatial / biomechanical reasoning.
For comparison queries both videos are analysed side-by-side.
Supports YouTube URLs and local files transparently.

Enhancements:
  - Injects sport-specific key metrics and common errors from
    ``SPORT_SPECIFIC_PROMPTS`` when the sport is recognised.
  - Filters analyses below ``CONFIDENCE_THRESHOLD``.
"""

from agents.base_agent import BaseAgent
from utils.gemini_client import GeminiClient
from config.settings import settings
from typing import Dict, Any, List


class AnalystAgent(BaseAgent):
    """Biomechanical analysis using Gemini's native video understanding."""

    def __init__(self, gemini_client: GeminiClient):
        super().__init__("Analyst")
        self.gemini_client = gemini_client

    async def _execute_impl(self, state: Dict[str, Any]) -> Dict[str, Any]:
        sources = state.get("video_sources", [])
        if not sources:
            self.log("error", "No videos provided")
            return {}

        user_query = state.get("user_query", "")
        sport = state.get("sport", "unknown")
        events_ctx = state.get("scouter_summary", "")

        if len(sources) >= 2:
            return await self._compare(sources, user_query, sport, events_ctx)
        return await self._single(sources[0], user_query, sport, events_ctx)

    # ── sport-specific context injection ──────────────────────────

    @staticmethod
    def _sport_context(sport: str) -> str:
        """Build an extra prompt section from SPORT_SPECIFIC_PROMPTS."""
        prompts = settings.SPORT_SPECIFIC_PROMPTS.get(sport.lower())
        if not prompts:
            return ""
        metrics = ", ".join(prompts.get("key_metrics", []))
        errors = ", ".join(prompts.get("common_errors", []))
        return (
            f"\n\nSport-specific guidance for {sport.upper()}:\n"
            f"  Key metrics to evaluate: {metrics}\n"
            f"  Common errors to watch for: {errors}\n"
        )

    # ── two-video comparison ──────────────────────────────────────

    async def _compare(
        self, sources: List[str], query: str, sport: str, events_ctx: str
    ) -> dict:
        self.log("info", f"Comparing: {sources[0]} vs {sources[1]}")

        ref1 = self.gemini_client.prepare_video(sources[0])
        ref2 = self.gemini_client.prepare_video(sources[1])

        sport_ctx = self._sport_context(sport)

        prompt = f"""
You are a professional {sport.upper()} biomechanist.

Previously detected events:
{events_ctx}
{sport_ctx}
User question: "{query}"

Compare the TWO videos (Video 1 = user, Video 2 = reference).
Analyse differences in:
1. Stance & posture
2. Footwork & movement patterns
3. Arm / racquet / bat positioning
4. Weight distribution & balance
5. Follow-through mechanics
6. Timing & rhythm

Return JSON:
{{
  "analyses": [
    {{
      "dimension": "e.g. knee_angle, arm_position, follow_through",
      "video1_observation": "what user does",
      "video2_observation": "what reference does",
      "delta_description": "key difference",
      "confidence": 0.0-1.0,
      "description": "detailed explanation",
      "recommendation": "how to improve"
    }}
  ],
  "summary": "Overall biomechanical comparison summary"
}}
"""
        result = self.gemini_client.query_two_videos_json(ref1, ref2, prompt)

        analyses = self._filter_by_confidence(result.get("analyses", []))

        return {
            "biomechanical_analysis": analyses,
            "analyst_summary": result.get("summary", ""),
        }

    # ── single-video form analysis ────────────────────────────────

    async def _single(
        self, source: str, query: str, sport: str, events_ctx: str
    ) -> dict:
        self.log("info", f"Analysing form: {source}")

        video_ref = self.gemini_client.prepare_video(source)

        sport_ctx = self._sport_context(sport)

        prompt = f"""
You are a professional {sport.upper()} biomechanist analysing an athlete's technique.

Previously detected events:
{events_ctx}
{sport_ctx}
User question: "{query}"

Evaluate the athlete's form and technique:
1. Stance & posture quality
2. Footwork efficiency
3. Arm mechanics & equipment handling
4. Weight transfer & balance
5. Follow-through
6. Timing & coordination

Return JSON:
{{
  "analyses": [
    {{
      "dimension": "e.g. knee_angle, arm_position",
      "observation": "what you see",
      "ideal": "what it should look like",
      "confidence": 0.0-1.0,
      "description": "detailed issue description",
      "recommendation": "specific improvement advice"
    }}
  ],
  "summary": "Overall form analysis summary"
}}
"""
        result = self.gemini_client.query_video_json(video_ref, prompt)

        analyses = self._filter_by_confidence(result.get("analyses", []))

        return {
            "biomechanical_analysis": analyses,
            "analyst_summary": result.get("summary", ""),
        }

    # ── confidence filter ─────────────────────────────────────────

    @staticmethod
    def _filter_by_confidence(analyses: list) -> list:
        """Drop analyses whose confidence is below CONFIDENCE_THRESHOLD."""
        threshold = settings.CONFIDENCE_THRESHOLD
        filtered = [
            a for a in analyses if a.get("confidence", 0) >= threshold
        ]
        return filtered
