"""InsightX — Interactive CLI.

Flow:
  1. User provides a video (local path or YouTube URL)
  2. User types a question / prompt
  3. Full multi-agent pipeline runs → prints coaching response
  4. User can ask follow-up questions (chat loop) that still reference the video
  5. Type 'quit' or 'new' to exit / start over
"""

import asyncio
import os
import sys
import logging

from config.settings import settings
from utils.gemini_client import GeminiClient
from workflows.insightx_workflow import InsightXWorkflow

# ── logging ───────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-22s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("insightx.main")


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║               InsightX — AI Sports Coach                     ║
║      Vision-Language-Action Multi-Agent Framework            ║
╚══════════════════════════════════════════════════════════════╝
"""


# ── helpers ───────────────────────────────────────────────────────────────

def resolve_video(source: str) -> str:
    """
    Validate a video source.
    - YouTube URL → returned as-is (Gemini accepts it directly)
    - Local file   → check it exists and return absolute path
    """
    if GeminiClient.is_youtube_url(source):
        return source.strip()

    path = os.path.abspath(source.strip().strip('"').strip("'"))
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Video file not found: {path}")
    return path


def print_response(text: str):
    print("\n" + "=" * 60)
    print("  InsightX Response")
    print("=" * 60)
    print(text)
    print("=" * 60 + "\n")


# ── main loop ─────────────────────────────────────────────────────────────

def main():
    print(BANNER)

    # --- API key ---
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        api_key = input("Enter your Gemini API key: ").strip()
        if not api_key:
            print("No API key provided. Exiting.")
            sys.exit(1)
        os.environ["GEMINI_API_KEY"] = api_key

    gemini = GeminiClient(api_key=api_key, model_name=settings.GEMINI_MODEL)
    workflow = InsightXWorkflow(gemini)

    while True:
        # --- video input ---
        print("\nProvide a video to analyse.")
        print("  • Paste a YouTube URL")
        print("  • Or enter a local file path")
        print("  • Type 'quit' to exit\n")

        source1 = input("Video source: ").strip()
        if source1.lower() in ("quit", "exit", "q"):
            break

        try:
            source1 = resolve_video(source1)
        except FileNotFoundError as e:
            print(f"  ✗ {e}")
            continue

        # optional second video for comparison
        source2_raw = input("Second video for comparison (Enter to skip): ").strip()
        sources = [source1]
        if source2_raw:
            try:
                sources.append(resolve_video(source2_raw))
            except FileNotFoundError as e:
                print(f"  ✗ {e} — continuing with one video")

        # sport hint
        sport = input("Sport (e.g. tennis, cricket, basketball — Enter to auto-detect): ").strip() or "unknown"

        # --- first query & pipeline ---
        print("\nWhat would you like to know about this video?")
        user_query = input("Your question: ").strip()
        if not user_query:
            print("  ✗ No question provided.")
            continue

        initial_state = {
            "user_query": user_query,
            "video_sources": sources,
            "sport": sport,
            "chat_history": [],
        }

        print("\nRunning analysis pipeline…  (this may take a minute)")
        try:
            result = workflow.run(initial_state)
        except Exception as e:
            logger.exception("Pipeline error")
            print(f"\n  ✗ Analysis failed: {e}")
            continue

        response_text = result.get("final_response", "No response generated.")
        print_response(response_text)

        # --- chat loop (follow-up questions referencing same video) ---
        print("You can now ask follow-up questions about the same video.")
        print("Type 'new' for a new video, 'quit' to exit.\n")

        # start a Gemini chat session seeded with the video
        video_ref = gemini.prepare_video(sources[0])
        system_instruction = (
            "You are InsightX, an expert AI sports coach. "
            "The athlete has uploaded a video and received the following analysis:\n\n"
            f"{response_text}\n\n"
            "Answer follow-up questions about the same video. "
            "Be specific, reference timestamps, and give actionable advice."
        )
        chat = gemini.start_chat(
            video_ref=video_ref,
            system_instruction=system_instruction,
        )

        while True:
            follow_up = input("Follow-up question: ").strip()
            if not follow_up:
                continue
            if follow_up.lower() in ("quit", "exit", "q"):
                gemini.cleanup_all()
                print("Goodbye!")
                sys.exit(0)
            if follow_up.lower() in ("new", "reset"):
                break

            try:
                reply = gemini.chat_message(chat, follow_up)
                print_response(reply)
            except Exception as e:
                logger.exception("Chat error")
                print(f"  ✗ Error: {e}")

        # cleanup before next video
        gemini.cleanup_all()

    gemini.cleanup_all()
    print("Goodbye!")


if __name__ == "__main__":
    main()
