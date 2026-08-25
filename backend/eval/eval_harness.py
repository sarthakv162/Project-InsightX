"""InsightX Evaluation Harness.

Measures the quality of the multi-agent pipeline against hand-annotated
ground-truth clips.  Three core metrics:

1. **Timestamp Precision** — fraction of returned ``key_events`` whose
   ``start_seconds`` lands within ±TOLERANCE of a real event.
2. **Hallucination Rate** — fraction of returned events that don't match
   any ground-truth event (lower is better).
3. **Recall / Completeness** — fraction of ground-truth events found by
   the pipeline.

Usage:
    python -m eval.run_eval --ground-truth eval/ground_truth.json
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# How close (in seconds) a predicted event must be to a ground-truth
# event to count as a match.
DEFAULT_TOLERANCE_SECONDS = 1.0


# ── Data structures ──────────────────────────────────────────────────────

@dataclass
class GroundTruthEvent:
    """A hand-annotated event from a video clip."""

    event_type: str
    start_seconds: float
    end_seconds: float
    description: str = ""


@dataclass
class GroundTruthClip:
    """A single annotated clip — one video + its ground-truth events."""

    clip_id: str
    video_source: str  # local path or YouTube URL
    sport: str
    query: str  # the question to ask the pipeline
    events: List[GroundTruthEvent] = field(default_factory=list)


@dataclass
class EvalResult:
    """Result of evaluating one clip."""

    clip_id: str
    gt_event_count: int
    predicted_event_count: int
    matched: int  # correctly detected (within tolerance)
    hallucinated: int  # predicted but no GT match
    missed: int  # GT events not detected

    @property
    def precision(self) -> float:
        """Fraction of predicted events that are real."""
        return self.matched / self.predicted_event_count if self.predicted_event_count else 0.0

    @property
    def recall(self) -> float:
        """Fraction of real events that were detected."""
        return self.matched / self.gt_event_count if self.gt_event_count else 0.0

    @property
    def hallucination_rate(self) -> float:
        """Fraction of predicted events that are hallucinated."""
        return self.hallucinated / self.predicted_event_count if self.predicted_event_count else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    def summary_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "gt_events": self.gt_event_count,
            "predicted_events": self.predicted_event_count,
            "matched": self.matched,
            "hallucinated": self.hallucinated,
            "missed": self.missed,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "hallucination_rate": round(self.hallucination_rate, 4),
            "f1": round(self.f1, 4),
        }


# ── Core evaluation logic ────────────────────────────────────────────────

def match_events(
    gt_events: List[GroundTruthEvent],
    predicted_events: List[Dict[str, Any]],
    tolerance: float = DEFAULT_TOLERANCE_SECONDS,
) -> EvalResult:
    """Match predicted events against ground-truth using timestamp proximity.

    A predicted event is "matched" if its ``start_seconds`` is within
    ±*tolerance* of any unmatched ground-truth event's ``start_seconds``.
    Each GT event can only be matched once (greedy, nearest-first).

    Args:
        gt_events: Hand-annotated ground-truth events.
        predicted_events: Events returned by the pipeline (list of dicts
            with at least ``start_seconds``).
        tolerance: Maximum seconds difference for a match.

    Returns:
        EvalResult with counts of matched, hallucinated, and missed events.
    """
    # Sort both lists by start_seconds for greedy matching
    gt_sorted = sorted(gt_events, key=lambda e: e.start_seconds)
    pred_sorted = sorted(
        predicted_events, key=lambda e: e.get("start_seconds", 0)
    )

    gt_matched = [False] * len(gt_sorted)
    pred_matched = [False] * len(pred_sorted)

    # Greedy nearest-first matching
    pairs: List[tuple] = []
    for pi, pred in enumerate(pred_sorted):
        pred_ts = pred.get("start_seconds", 0)
        best_gi = -1
        best_dist = float("inf")
        for gi, gt in enumerate(gt_sorted):
            if gt_matched[gi]:
                continue
            dist = abs(pred_ts - gt.start_seconds)
            if dist <= tolerance and dist < best_dist:
                best_dist = dist
                best_gi = gi
        if best_gi >= 0:
            pairs.append((pi, best_gi, best_dist))
            pred_matched[pi] = True
            gt_matched[best_gi] = True

    matched = len(pairs)
    hallucinated = sum(1 for m in pred_matched if not m)
    missed = sum(1 for m in gt_matched if not m)

    return EvalResult(
        clip_id="",
        gt_event_count=len(gt_sorted),
        predicted_event_count=len(pred_sorted),
        matched=matched,
        hallucinated=hallucinated,
        missed=missed,
    )


def evaluate_clip(
    clip: GroundTruthClip,
    pipeline_fn,
    tolerance: float = DEFAULT_TOLERANCE_SECONDS,
) -> EvalResult:
    """Run the pipeline on a clip and evaluate against ground-truth.

    Args:
        clip: Annotated clip with video source, query, and GT events.
        pipeline_fn: Callable that takes (video_source, query, sport)
            and returns a dict with "key_events" list.
        tolerance: Seconds tolerance for timestamp matching.

    Returns:
        EvalResult for this clip.
    """
    logger.info(f"Evaluating clip: {clip.clip_id}")

    result = pipeline_fn(clip.video_source, clip.query, clip.sport)
    predicted = result.get("key_events", [])

    eval_result = match_events(clip.events, predicted, tolerance)
    eval_result.clip_id = clip.clip_id

    logger.info(
        f"  {clip.clip_id}: precision={eval_result.precision:.2%}, "
        f"recall={eval_result.recall:.2%}, "
        f"hallucination={eval_result.hallucination_rate:.2%}"
    )
    return eval_result


def aggregate_results(results: List[EvalResult]) -> Dict[str, Any]:
    """Aggregate multiple clip results into overall metrics."""
    total_gt = sum(r.gt_event_count for r in results)
    total_pred = sum(r.predicted_event_count for r in results)
    total_matched = sum(r.matched for r in results)
    total_hallucinated = sum(r.hallucinated for r in results)
    total_missed = sum(r.missed for r in results)

    precision = total_matched / total_pred if total_pred else 0.0
    recall = total_matched / total_gt if total_gt else 0.0
    hallucination_rate = total_hallucinated / total_pred if total_pred else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "num_clips": len(results),
        "total_gt_events": total_gt,
        "total_predicted_events": total_pred,
        "total_matched": total_matched,
        "total_hallucinated": total_hallucinated,
        "total_missed": total_missed,
        "aggregate_precision": round(precision, 4),
        "aggregate_recall": round(recall, 4),
        "aggregate_hallucination_rate": round(hallucination_rate, 4),
        "aggregate_f1": round(f1, 4),
        "per_clip": [r.summary_dict() for r in results],
    }


# ── Ground-truth loading ─────────────────────────────────────────────────

def load_ground_truth(path: str) -> List[GroundTruthClip]:
    """Load ground-truth clips from a JSON file.

    Expected format — see ``eval/ground_truth.json`` for schema.
    """
    with open(path) as f:
        data = json.load(f)

    clips = []
    for entry in data.get("clips", []):
        events = [
            GroundTruthEvent(
                event_type=e["event_type"],
                start_seconds=e["start_seconds"],
                end_seconds=e["end_seconds"],
                description=e.get("description", ""),
            )
            for e in entry.get("events", [])
        ]
        clips.append(
            GroundTruthClip(
                clip_id=entry["clip_id"],
                video_source=entry["video_source"],
                sport=entry.get("sport", "unknown"),
                query=entry.get("query", "Analyse this video"),
                events=events,
            )
        )
    return clips
