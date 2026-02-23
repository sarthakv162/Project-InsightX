"""InsightX LangGraph Workflow — Multi-Agent Sports Analysis Pipeline.

Graph structure:
    START → orchestrator → route_by_type → scouter → analyst → strategist
                                              ↘ (learning) → coach
                                      → synthesizer → END

Supports YouTube URLs and local files transparently via ``prepare_video()``.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from langgraph.graph import StateGraph, END

from agents.orchestrator import OrchestratorAgent
from agents.scouter import ScouterAgent
from agents.analyst import AnalystAgent
from agents.strategist import StrategistAgent
from agents.coach import CoachAgent
from models.data_models import GraphState
from utils.gemini_client import GeminiClient
from config.settings import settings

logger = logging.getLogger(__name__)


# ── Workflow class ────────────────────────────────────────────────────────

class InsightXWorkflow:
    """Builds and compiles the LangGraph state-machine."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini = gemini_client

        # instantiate agents once
        self.orchestrator = OrchestratorAgent(gemini_client)
        self.scouter = ScouterAgent(gemini_client)
        self.analyst = AnalystAgent(gemini_client)
        self.strategist = StrategistAgent(gemini_client)
        self.coach = CoachAgent(gemini_client)

        self.graph = self._build_graph()

    # ── graph construction ────────────────────────────────────────

    def _build_graph(self):
        g = StateGraph(GraphState)

        # nodes
        g.add_node("orchestrator", self._run_orchestrator)
        g.add_node("scouter", self._run_scouter)
        g.add_node("analyst", self._run_analyst)
        g.add_node("strategist", self._run_strategist)
        g.add_node("coach", self._run_coach)
        g.add_node("synthesizer", self._run_synthesizer)

        # edges
        g.set_entry_point("orchestrator")
        g.add_conditional_edges(
            "orchestrator",
            self._route_after_orchestrator,
            {
                "scouter": "scouter",
                "analyst": "analyst",
            },
        )
        g.add_edge("scouter", "analyst")
        g.add_edge("analyst", "strategist")
        g.add_conditional_edges(
            "strategist",
            self._route_after_strategist,
            {
                "coach": "coach",
                "synthesizer": "synthesizer",
            },
        )
        g.add_edge("coach", "synthesizer")
        g.add_edge("synthesizer", END)

        return g.compile()

    # ── routing functions ─────────────────────────────────────────

    @staticmethod
    def _route_after_orchestrator(state: Dict[str, Any]) -> str:
        qt = state.get("query_type", "general_analysis")
        if qt == "comparison":
            return "analyst"     # skip scouter for pure comparisons
        return "scouter"

    @staticmethod
    def _route_after_strategist(state: Dict[str, Any]) -> str:
        qt = state.get("query_type", "general_analysis")
        if qt in ("learning_plan",):
            return "coach"
        return "synthesizer"

    # ── node wrappers (sync → async bridge) ───────────────────────

    def _run_orchestrator(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.orchestrator.execute(state)
        )

    def _run_scouter(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.scouter.execute(state)
        )

    def _run_analyst(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.analyst.execute(state)
        )

    def _run_strategist(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.strategist.execute(state)
        )

    def _run_coach(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(
            self.coach.execute(state)
        )

    def _run_synthesizer(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Final node — turns agent outputs into a clear coaching response."""
        summaries = []
        for key in ("scouter_summary", "analyst_summary", "strategist_summary", "coach_summary"):
            s = state.get(key)
            if s:
                summaries.append(f"### {key.replace('_', ' ').title()}\n{s}")

        context = "\n\n".join(summaries) or "No analysis context available."

        prompt = f"""
You are an elite sports coach delivering a clear, detailed response
to the athlete's request.

Athlete's question: "{state.get('user_query', '')}"

Here is the analysis from your team:

{context}

Rules:
- Use markdown formatting for readability (headers, bullets, bold)
- Start with the direct answer to the question
- Be specific — reference timestamps, techniques, and observations
- End with 2-3 actionable next-step recommendations
- Keep tone encouraging yet honest
"""
        response = self.gemini.text_query(prompt)
        return {"final_response": response}

    # ── public API ────────────────────────────────────────────────

    def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline synchronously and return final state."""
        logger.info("▶ Starting InsightX pipeline")
        result = self.graph.invoke(initial_state)
        logger.info("✔ Pipeline complete")
        return result


# ── convenience factory ───────────────────────────────────────────────────

def create_workflow(api_key: str | None = None) -> InsightXWorkflow:
    key = api_key or settings.GEMINI_API_KEY
    if not key:
        raise ValueError("GEMINI_API_KEY not set")
    client = GeminiClient(api_key=key, model_name=settings.GEMINI_MODEL)
    return InsightXWorkflow(client)
