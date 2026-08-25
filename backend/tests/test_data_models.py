"""Tests for data models and enums."""

import pytest
from models.data_models import (
    QueryType,
    SportType,
    Timestamp,
    KeyEvent,
    BiomechanicalAnalysis,
    GraphState,
)


class TestQueryType:
    def test_valid_values(self):
        assert QueryType("error_analysis") == QueryType.ERROR_ANALYSIS
        assert QueryType("comparison") == QueryType.COMPARISON
        assert QueryType("learning_plan") == QueryType.LEARNING_PLAN

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            QueryType("invalid_type")

    def test_all_types_exist(self):
        expected = {
            "error_analysis",
            "comparison",
            "learning_plan",
            "opponent_strategy",
            "event_location",
            "general_analysis",
        }
        actual = {qt.value for qt in QueryType}
        assert actual == expected


class TestSportType:
    def test_valid_sports(self):
        assert SportType("cricket") == SportType.CRICKET
        assert SportType("unknown") == SportType.UNKNOWN

    def test_all_sports(self):
        assert len(SportType) >= 7  # including UNKNOWN


class TestTimestamp:
    def test_duration(self):
        ts = Timestamp(start_seconds=10.0, end_seconds=15.5)
        assert ts.duration == pytest.approx(5.5)

    def test_zero_duration(self):
        ts = Timestamp(start_seconds=5.0, end_seconds=5.0)
        assert ts.duration == 0.0


class TestKeyEvent:
    def test_creation(self):
        event = KeyEvent(
            event_type="serve",
            timestamp=Timestamp(start_seconds=1.0, end_seconds=3.0),
            confidence=0.9,
            description="Strong first serve",
            visual_indicators=["high toss", "full extension"],
        )
        assert event.event_type == "serve"
        assert event.confidence == 0.9
        assert len(event.visual_indicators) == 2

    def test_default_visual_indicators(self):
        event = KeyEvent(
            event_type="shot",
            timestamp=Timestamp(start_seconds=0, end_seconds=1),
            confidence=0.5,
            description="Test",
        )
        assert event.visual_indicators == []
