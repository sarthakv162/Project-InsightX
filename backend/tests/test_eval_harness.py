"""Tests for the evaluation harness — no API calls required.

Verifies the core event-matching logic that underpins the
timestamp precision and hallucination rate metrics.
"""

import pytest
from eval.eval_harness import (
    GroundTruthEvent,
    match_events,
    EvalResult,
    aggregate_results,
)


class TestMatchEvents:
    """Test the greedy nearest-first event matching."""

    def _make_gt(self, start: float, end: float = None) -> GroundTruthEvent:
        return GroundTruthEvent(
            event_type="test",
            start_seconds=start,
            end_seconds=end or start + 2.0,
        )

    def _make_pred(self, start: float) -> dict:
        return {"start_seconds": start, "event_type": "test"}

    def test_perfect_match(self):
        gt = [self._make_gt(5.0), self._make_gt(10.0)]
        pred = [self._make_pred(5.0), self._make_pred(10.0)]
        result = match_events(gt, pred, tolerance=1.0)
        assert result.matched == 2
        assert result.hallucinated == 0
        assert result.missed == 0

    def test_within_tolerance(self):
        gt = [self._make_gt(5.0)]
        pred = [self._make_pred(5.8)]  # within 1s
        result = match_events(gt, pred, tolerance=1.0)
        assert result.matched == 1
        assert result.precision == 1.0

    def test_outside_tolerance(self):
        gt = [self._make_gt(5.0)]
        pred = [self._make_pred(7.0)]  # >1s away
        result = match_events(gt, pred, tolerance=1.0)
        assert result.matched == 0
        assert result.hallucinated == 1
        assert result.missed == 1

    def test_hallucination(self):
        gt = [self._make_gt(5.0)]
        pred = [self._make_pred(5.0), self._make_pred(20.0)]
        result = match_events(gt, pred, tolerance=1.0)
        assert result.matched == 1
        assert result.hallucinated == 1
        assert result.hallucination_rate == pytest.approx(0.5)

    def test_missed_events(self):
        gt = [self._make_gt(5.0), self._make_gt(10.0)]
        pred = [self._make_pred(5.0)]
        result = match_events(gt, pred, tolerance=1.0)
        assert result.matched == 1
        assert result.missed == 1
        assert result.recall == pytest.approx(0.5)

    def test_empty_predictions(self):
        gt = [self._make_gt(5.0)]
        pred = []
        result = match_events(gt, pred, tolerance=1.0)
        assert result.matched == 0
        assert result.missed == 1
        assert result.precision == 0.0

    def test_empty_ground_truth(self):
        gt = []
        pred = [self._make_pred(5.0)]
        result = match_events(gt, pred, tolerance=1.0)
        assert result.hallucinated == 1
        assert result.recall == 0.0

    def test_both_empty(self):
        result = match_events([], [], tolerance=1.0)
        assert result.matched == 0
        assert result.precision == 0.0
        assert result.recall == 0.0


class TestEvalResult:
    def test_f1_score(self):
        r = EvalResult(
            clip_id="test",
            gt_event_count=10,
            predicted_event_count=8,
            matched=6,
            hallucinated=2,
            missed=4,
        )
        assert r.precision == pytest.approx(6 / 8)
        assert r.recall == pytest.approx(6 / 10)
        assert r.f1 > 0

    def test_summary_dict(self):
        r = EvalResult("test", 5, 5, 4, 1, 1)
        d = r.summary_dict()
        assert d["clip_id"] == "test"
        assert "precision" in d
        assert "hallucination_rate" in d


class TestAggregateResults:
    def test_aggregate_two_clips(self):
        r1 = EvalResult("a", gt_event_count=5, predicted_event_count=4, matched=3, hallucinated=1, missed=2)
        r2 = EvalResult("b", gt_event_count=3, predicted_event_count=3, matched=2, hallucinated=1, missed=1)
        agg = aggregate_results([r1, r2])
        assert agg["num_clips"] == 2
        assert agg["total_matched"] == 5
        assert agg["total_hallucinated"] == 2
        assert agg["aggregate_precision"] == pytest.approx(5 / 7, rel=1e-2)
