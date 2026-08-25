"""Coach Agent — Pedagogical Mentor & Learning Plan Generation."""

from agents.base_agent import BaseAgent
from utils.gemini_client import GeminiClient
from typing import Dict, Any


class CoachAgent(BaseAgent):
    """
    Translates analysis into actionable coaching plans and drills.
    Uses accumulated context from all previous agents.
    """

    def __init__(self, gemini_client: GeminiClient):
        super().__init__("Coach")
        self.gemini_client = gemini_client

    async def _execute_impl(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        sport = state.get("sport", "unknown")

        scouter_ctx = state.get("scouter_summary", "")
        analyst_ctx = state.get("analyst_summary", "")
        strategist_ctx = state.get("strategist_summary", "")

        self.log("info", "Generating coaching plan")

        prompt = f"""
You are an expert {sport.upper()} coach creating a personalised training plan.

=== Event Analysis ===
{scouter_ctx or "None"}

=== Biomechanical Analysis ===
{analyst_ctx or "None"}

=== Tactical Analysis ===
{strategist_ctx or "None"}

Player's question / goal: "{user_query}"

Create a structured learning plan:
1. Target skill / area of improvement
2. 4-week progressive programme
3. 3-5 specific drills with step-by-step instructions
4. Measurable milestones
5. Make it realistic, progressive, and motivating

Return JSON:
{{
  "title": "Plan title",
  "target_skill": "main focus area",
  "duration_weeks": 4,
  "weekly_focus": ["week 1 focus", "week 2 focus", "week 3 focus", "week 4 focus"],
  "drills": [
    {{
      "name": "drill name",
      "duration_minutes": 15,
      "description": "what to do",
      "steps": ["step 1", "step 2"],
      "repetitions": 10,
      "focus_area": "area",
      "difficulty": "beginner | intermediate | advanced"
    }}
  ],
  "milestones": ["week 1 goal", "week 2 goal", "week 3 goal", "week 4 goal"],
  "progression_notes": "how difficulty ramps up",
  "summary": "Motivational overview of the plan"
}}
"""

        result = self.gemini_client.text_query_json(prompt)
        summary = result.get("summary", "")

        self.log("info", f"Plan created: {result.get('title', 'N/A')}")

        return {
            "coaching_plan": result,
            "coach_summary": summary,
        }
