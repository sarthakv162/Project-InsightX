"""Run InsightX evaluation.

Usage:
    cd backend
    python -m eval.run_eval --ground-truth eval/ground_truth.json

Requires a GEMINI_API_KEY in the environment.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure backend is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from utils.gemini_client import GeminiClient
from workflows.insightx_workflow import InsightXWorkflow
from eval.eval_harness import (
    load_ground_truth,
    evaluate_clip,
    aggregate_results,
    DEFAULT_TOLERANCE_SECONDS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-22s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("insightx.eval")


def main():
    parser = argparse.ArgumentParser(description="InsightX Evaluation Harness")
    parser.add_argument(
        "--ground-truth",
        type=str,
        default="eval/ground_truth.json",
        help="Path to ground-truth JSON file",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE_SECONDS,
        help=f"Timestamp tolerance in seconds (default {DEFAULT_TOLERANCE_SECONDS})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write JSON results (default: stdout)",
    )
    args = parser.parse_args()

    # Load ground truth
    clips = load_ground_truth(args.ground_truth)
    logger.info(f"Loaded {len(clips)} annotated clips")

    if not clips:
        logger.error("No clips found — check your ground_truth.json")
        sys.exit(1)

    # Build pipeline
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY not set")
        sys.exit(1)

    client = GeminiClient(api_key=api_key, model_name=settings.GEMINI_MODEL)
    workflow = InsightXWorkflow(client)

    def pipeline_fn(video_source: str, query: str, sport: str):
        initial_state = {
            "user_query": query,
            "video_sources": [video_source],
            "sport": sport,
            "chat_history": [],
        }
        return workflow.run(initial_state)

    # Evaluate each clip
    results = []
    for clip in clips:
        try:
            result = evaluate_clip(clip, pipeline_fn, tolerance=args.tolerance)
            results.append(result)
        except Exception as exc:
            logger.error(f"Failed on clip {clip.clip_id}: {exc}")

    # Aggregate and report
    if not results:
        logger.error("No clips evaluated successfully")
        sys.exit(1)

    report = aggregate_results(results)

    # Print summary
    print("\n" + "=" * 60)
    print("  InsightX Evaluation Report")
    print("=" * 60)
    print(f"  Clips evaluated:       {report['num_clips']}")
    print(f"  Total GT events:       {report['total_gt_events']}")
    print(f"  Total predicted:       {report['total_predicted_events']}")
    print(f"  Matched:               {report['total_matched']}")
    print(f"  Hallucinated:          {report['total_hallucinated']}")
    print(f"  Missed:                {report['total_missed']}")
    print(f"  ─────────────────────────────")
    print(f"  Precision:             {report['aggregate_precision']:.2%}")
    print(f"  Recall:                {report['aggregate_recall']:.2%}")
    print(f"  Hallucination rate:    {report['aggregate_hallucination_rate']:.2%}")
    print(f"  F1:                    {report['aggregate_f1']:.2%}")
    print("=" * 60)

    # Save JSON
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))
        logger.info(f"Results saved to {args.output}")
    else:
        print("\nFull JSON report:")
        print(json.dumps(report, indent=2))

    # Cleanup
    client.cleanup_all()


if __name__ == "__main__":
    main()
