"""Tests for workflow graph construction and routing.

These tests verify the LangGraph state machine without making
any Gemini API calls.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from models.data_models import GraphState


class TestWorkflowRouting:
    """Test the routing logic without building a real workflow."""

    def test_route_after_orchestrator_always_scouter(self):
        from workflows.insightx_workflow import InsightXWorkflow

        state = {"query_type": "general_analysis"}
        result = InsightXWorkflow._route_after_orchestrator(state)
        assert result == "scouter"

    def test_route_after_strategist_learning_plan(self):
        from workflows.insightx_workflow import InsightXWorkflow

        state = {"query_type": "learning_plan"}
        result = InsightXWorkflow._route_after_strategist(state)
        assert result == "coach"

    def test_route_after_strategist_default(self):
        from workflows.insightx_workflow import InsightXWorkflow

        state = {"query_type": "general_analysis"}
        result = InsightXWorkflow._route_after_strategist(state)
        assert result == "synthesizer"


class TestOrchestratorSequence:
    """Test the agent sequence determination."""

    def test_error_analysis_sequence(self):
        from agents.orchestrator import OrchestratorAgent

        seq = OrchestratorAgent.determine_agent_sequence("error_analysis")
        assert seq == ["scouter", "analyst", "strategist"]

    def test_learning_plan_includes_coach(self):
        from agents.orchestrator import OrchestratorAgent

        seq = OrchestratorAgent.determine_agent_sequence("learning_plan")
        assert "coach" in seq

    def test_unknown_type_falls_back(self):
        from agents.orchestrator import OrchestratorAgent

        seq = OrchestratorAgent.determine_agent_sequence("unknown_type_xyz")
        assert len(seq) > 0  # Should return default sequence


class TestSettings:
    """Verify all settings are properly defined and have sensible defaults."""

    def test_all_settings_exist(self):
        from config.settings import settings

        # These must all exist and be non-None
        assert settings.GEMINI_MODEL
        assert settings.VIDEO_MAX_DURATION > 0
        assert settings.VIDEO_SAMPLE_FPS > 0
        assert settings.VIDEO_BURST_FPS > 0
        assert settings.FRAME_QUALITY > 0
        assert settings.AGENT_TIMEOUT > 0
        assert settings.MAX_RETRIES > 0
        assert 0 < settings.CONFIDENCE_THRESHOLD < 1
        assert settings.EVENT_DURATION_MIN_SECONDS >= 0
        assert settings.CACHE_TTL_MINUTES > 0

    def test_sport_specific_prompts_structure(self):
        from config.settings import settings

        for sport, prompts in settings.SPORT_SPECIFIC_PROMPTS.items():
            assert "key_metrics" in prompts, f"{sport} missing key_metrics"
            assert "common_errors" in prompts, f"{sport} missing common_errors"
            assert len(prompts["key_metrics"]) >= 3
            assert len(prompts["common_errors"]) >= 2
