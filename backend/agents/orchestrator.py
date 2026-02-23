"""Orchestrator Agent — classifies queries and routes agents."""

from agents.base_agent import BaseAgent
from models.data_models import QueryType
from utils.gemini_client import GeminiClient
from typing import Dict, Any


class OrchestratorAgent(BaseAgent):
    """
    Receives the user query and determines:
    1. Query type (error_analysis, comparison, learning_plan, …)
    2. Whether clarification is needed before proceeding
    """

    def __init__(self, gemini_client: GeminiClient):
        super().__init__("Orchestrator")
        self.gemini_client = gemini_client

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_query = state.get("user_query", "")
        sport = state.get("sport", "unknown")

        self.log("info", f"Classifying query: {user_query}")

        analysis = self._classify_query(user_query, sport)

        # Safely convert string → QueryType enum value
        raw_type = analysis.get("query_type", "general_analysis")
        try:
            qt = QueryType(raw_type)
        except ValueError:
            qt = QueryType.GENERAL_ANALYSIS

        return {
            "query_type": qt.value,
            "clarification_required": analysis.get("needs_clarification", False),
            "clarification_questions": analysis.get("clarifications", []),
            "confidence_level": analysis.get("confidence", 0.8),
        }

    def _classify_query(self, query: str, sport: str) -> Dict[str, Any]:
        prompt = f"""Classify this sports analysis query. A video has already been provided.

Query: "{query}"
Sport: {sport}

Return JSON:
{{
  "query_type": "error_analysis | comparison | learning_plan | opponent_strategy | event_location | general_analysis",
  "confidence": 0.0-1.0,
  "needs_clarification": false,
  "clarifications": []
}}

Pick exactly ONE query_type value from the list.
Almost always set needs_clarification to false — the user has already provided a video and a question.
"""
        return self.gemini_client.text_query_json(prompt)

    @staticmethod
    def determine_agent_sequence(query_type: str) -> list:
        sequences = {
            "error_analysis": ["scouter", "analyst", "strategist"],
            "comparison": ["analyst", "strategist"],
            "learning_plan": ["scouter", "analyst", "strategist", "coach"],
            "opponent_strategy": ["scouter", "strategist"],
            "event_location": ["scouter"],
            "general_analysis": ["scouter", "analyst", "strategist"],
        }
        return sequences.get(query_type, ["scouter", "analyst", "strategist"])
