"""Strategist Agent — Tactical Reasoning & Strategy Analysis."""

from agents.base_agent import BaseAgent
from utils.gemini_client import GeminiClient
from typing import Dict, Any


class StrategistAgent(BaseAgent):
    """
    Analyses the tactical and strategic layer of the game.
    Uses context from Scouter and Analyst plus the video itself.
    """

    def __init__(self, gemini_client: GeminiClient):
        super().__init__("Strategist")
        self.gemini_client = gemini_client

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        sources = state.get("video_sources", [])
        user_query = state.get("user_query", "")
        sport = state.get("sport", "unknown")

        scouter_ctx = state.get("scouter_summary", "")
        analyst_ctx = state.get("analyst_summary", "")
        events = state.get("key_events", [])
        analyses = state.get("biomechanical_analysis", [])

        self.log(
            "info",
            f"Analysing strategy — {len(events)} events, {len(analyses)} biomech findings",
        )

        prompt = self._build_prompt(user_query, sport, scouter_ctx, analyst_ctx)

        # Query video for richer tactical reasoning
        if sources:
            video_ref = self.gemini_client.prepare_video(sources[0])
            result = self.gemini_client.query_video_json(video_ref, prompt)
        else:
            result = self.gemini_client.text_query_json(prompt)

        insights = result.get("insights", [])
        summary = result.get("overall_analysis", "")

        self.log("info", f"Generated {len(insights)} tactical insights")

        return {
            "tactical_insights": insights,
            "strategist_summary": summary,
        }

    def _build_prompt(
        self, query: str, sport: str, scouter_ctx: str, analyst_ctx: str
    ) -> str:
        return f"""
You are a professional {sport.upper()} strategist and tactical analyst.

=== Context from event detection ===
{scouter_ctx or "No events detected yet."}

=== Context from biomechanical analysis ===
{analyst_ctx or "No biomechanical analysis yet."}

User question: "{query}"

Analyse the tactical and strategic aspects:
1. What strategic approach was used?
2. Where were the tactical mistakes?
3. How could the opponent have exploited weaknesses?
4. Root cause of any failure or lost point
5. Strategic adjustments to recommend

Return JSON:
{{
  "insights": [
    {{
      "insight_type": "positioning_error | timing_mistake | strategy_mismatch | shot_selection | court_management | other",
      "confidence": 0.0-1.0,
      "description": "detailed tactical issue",
      "opposing_strategy": "what opponent did or could do",
      "why_it_failed": "root cause",
      "correction_strategy": "what to do instead"
    }}
  ],
  "overall_analysis": "comprehensive tactical summary"
}}
"""
