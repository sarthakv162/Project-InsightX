"""Compare single-prompt vs multi-agent hallucination rates.

This script runs the same clips through two modes:
1. **Single-prompt** — one mega-prompt asking for everything at once
2. **Multi-agent** — the full Scouter→Analyst→Strategist pipeline

The difference in hallucination rates is the evidence for the claim
that multi-agent decomposition reduces hallucinations.

Usage:
    cd backend
    python -m eval.compare_modes --ground-truth eval/ground_truth.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from utils.gemini_client import GeminiClient
from eval.eval_harness import (
    load_ground_truth,
    match_events,
    aggregate_results,
    EvalResult,
    DEFAULT_TOLERANCE_SECONDS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("insightx.compare_modes")


SINGLE_PROMPT_TEMPLATE = """
You are an expert {sport} analyst.

Watch the entire video carefully and answer: "{query}"

Return a comprehensive JSON response with ALL of the following in a single pass:
{{
  "events": [
    {{
      "event_type": "type",
      "timestamp": "MM:SS",
      "start_seconds": 0.0,
      "end_seconds": 0.0,
      "confidence": 0.0-1.0,
      "description": "what happened"
    }}
  ],
  "biomechanical_analysis": [
    {{
      "dimension": "aspect analysed",
      "observation": "what you see",
      "confidence": 0.0-1.0,
      "recommendation": "how to improve"
    }}
  ],
  "tactical_analysis": "overall tactical summary",
  "summary": "complete analysis"
}}
"""


def run_single_prompt(client: GeminiClient, video_source: str, query: str, sport: str):
    """Run a single mega-prompt (no agent decomposition)."""
    video_ref = client.prepare_video(video_source)
    prompt = SINGLE_PROMPT_TEMPLATE.format(sport=sport, query=query)
    result = client.query_video_json(video_ref, prompt)
    return result


def run_multi_agent(workflow, video_source: str, query: str, sport: str):
    """Run the full multi-agent pipeline."""
    from workflows.insightx_workflow import InsightXWorkflow

    initial_state = {
        "user_query": query,
        "video_sources": [video_source],
        "sport": sport,
        "chat_history": [],
    }
    return workflow.run(initial_state)


def main():
    parser = argparse.ArgumentParser(
        description="Compare single-prompt vs multi-agent hallucination rates"
    )
    parser.add_argument(
        "--ground-truth", type=str, default="eval/ground_truth.json"
    )
    parser.add_argument(
        "--tolerance", type=float, default=DEFAULT_TOLERANCE_SECONDS
    )
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    clips = load_ground_truth(args.ground_truth)
    if not clips:
        logger.error("No clips found")
        sys.exit(1)

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY not set")
        sys.exit(1)

    client = GeminiClient(api_key=api_key, model_name=settings.GEMINI_MODEL)

    from workflows.insightx_workflow import InsightXWorkflow

    workflow = InsightXWorkflow(client)

    single_results = []
    multi_results = []

    for clip in clips:
        logger.info(f"\n{'='*40}\nClip: {clip.clip_id}\n{'='*40}")

        try:
            # Single prompt mode
            logger.info("Running SINGLE-PROMPT mode…")
            single_output = run_single_prompt(
                client, clip.video_source, clip.query, clip.sport
            )
            single_events = single_output.get("events", [])
            sr = match_events(clip.events, single_events, args.tolerance)
            sr.clip_id = f"{clip.clip_id}_single"
            single_results.append(sr)
            logger.info(
                f"  Single: {sr.precision:.0%} precision, "
                f"{sr.hallucination_rate:.0%} hallucination"
            )
        except Exception as e:
            logger.error(f"  Single-prompt failed: {e}")

        try:
            # Multi-agent mode
            logger.info("Running MULTI-AGENT mode…")
            multi_output = run_multi_agent(
                workflow, clip.video_source, clip.query, clip.sport
            )
            multi_events = multi_output.get("key_events", [])
            mr = match_events(clip.events, multi_events, args.tolerance)
            mr.clip_id = f"{clip.clip_id}_multi"
            multi_results.append(mr)
            logger.info(
                f"  Multi:  {mr.precision:.0%} precision, "
                f"{mr.hallucination_rate:.0%} hallucination"
            )
        except Exception as e:
            logger.error(f"  Multi-agent failed: {e}")

    # Aggregate
    single_agg = aggregate_results(single_results) if single_results else {}
    multi_agg = aggregate_results(multi_results) if multi_results else {}

    print("\n" + "=" * 60)
    print("  MODE COMPARISON REPORT")
    print("=" * 60)
    if single_agg:
        print(f"\n  SINGLE-PROMPT:")
        print(f"    Hallucination rate: {single_agg.get('aggregate_hallucination_rate', 0):.2%}")
        print(f"    Precision:          {single_agg.get('aggregate_precision', 0):.2%}")
        print(f"    Recall:             {single_agg.get('aggregate_recall', 0):.2%}")
    if multi_agg:
        print(f"\n  MULTI-AGENT:")
        print(f"    Hallucination rate: {multi_agg.get('aggregate_hallucination_rate', 0):.2%}")
        print(f"    Precision:          {multi_agg.get('aggregate_precision', 0):.2%}")
        print(f"    Recall:             {multi_agg.get('aggregate_recall', 0):.2%}")
    if single_agg and multi_agg:
        delta = (
            single_agg.get("aggregate_hallucination_rate", 0)
            - multi_agg.get("aggregate_hallucination_rate", 0)
        )
        print(f"\n  Hallucination reduction: {delta:.2%}")
    print("=" * 60)

    report = {
        "single_prompt": single_agg,
        "multi_agent": multi_agg,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2))
        logger.info(f"Results saved to {args.output}")

    client.cleanup_all()


if __name__ == "__main__":
    main()
