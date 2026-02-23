"""Gemini API client — using the new google-genai SDK.

Key features:
  - Native YouTube URL support (no download needed)
  - File API for local video uploads
  - Multi-turn chat with video context
  - Async support via client.aio
"""

from google import genai
from google.genai import types
import json
import re
import logging
from typing import Optional, Dict, List, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client wrapping the google-genai SDK for video understanding.

    Supports two video input modes:
      1. **YouTube URL** — passed directly to Gemini (no download)
      2. **Local file** — uploaded via File API once, reused across queries
    """

    YOUTUBE_RE = re.compile(
        r"(https?://)?(www\.)?"
        r"(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)"
        r"[\w\-]+"
    )

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self._uploaded_files: Dict[str, Any] = {}   # local path → File obj

    # ── video reference helpers ───────────────────────────────────

    @classmethod
    def is_youtube_url(cls, source: str) -> bool:
        return bool(cls.YOUTUBE_RE.search(source))

    def prepare_video(self, source: str):
        """
        Accept a local path **or** YouTube URL and return a reference
        usable in generate_content / chat.send_message.

        - YouTube URL → types.Part with file_data pointing at the URI
        - Local file  → uploaded File object (cached)
        """
        if self.is_youtube_url(source):
            logger.info(f"Using YouTube URL directly: {source}")
            return types.Part(
                file_data=types.FileData(file_uri=source)
            )
        return self._upload_local(source)

    def _upload_local(self, path: str):
        """Upload a local video file via File API (cached)."""
        if path in self._uploaded_files:
            logger.info(f"Video already uploaded: {path}")
            return self._uploaded_files[path]

        logger.info(f"Uploading video to Gemini: {path}")
        file_obj = self.client.files.upload(file=path)
        logger.info(f"Upload complete: {file_obj.name}")
        self._uploaded_files[path] = file_obj
        return file_obj

    def get_video_ref(self, source: str):
        """Return cached video ref or None."""
        if self.is_youtube_url(source):
            return types.Part(
                file_data=types.FileData(file_uri=source)
            )
        return self._uploaded_files.get(source)

    # ── core generation ───────────────────────────────────────────

    def query_video(self, video_ref, prompt: str) -> str:
        """Query a single video (uploaded file or YouTube Part)."""
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=[video_ref, prompt],
        )
        return resp.text

    def query_two_videos(self, ref1, ref2, prompt: str) -> str:
        """Compare two video references."""
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=[ref1, ref2, prompt],
        )
        return resp.text

    def text_query(self, prompt: str) -> str:
        """Text-only query (no media)."""
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return resp.text

    # ── JSON wrappers ─────────────────────────────────────────────

    def query_video_json(self, video_ref, prompt: str) -> Dict[str, Any]:
        return self._extract_json(self.query_video(video_ref, prompt))

    def query_two_videos_json(self, ref1, ref2, prompt: str) -> Dict[str, Any]:
        return self._extract_json(self.query_two_videos(ref1, ref2, prompt))

    def text_query_json(self, prompt: str) -> Dict[str, Any]:
        return self._extract_json(self.text_query(prompt))

    # ── multi-turn chat ───────────────────────────────────────────

    def start_chat(
        self,
        video_ref=None,
        system_instruction: str = None,
    ):
        """
        Create a multi-turn chat session.
        If *video_ref* is provided the video is seeded as the first message
        so all follow-ups can reference it.
        """
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
            )

        chat = self.client.chats.create(
            model=self.model_name,
            config=config,
        )

        if video_ref:
            chat.send_message(
                message=[video_ref, "I've uploaded a sports video for analysis. Acknowledge receipt briefly."]
            )

        return chat

    def chat_message(self, chat_session, message: str) -> str:
        """Send a follow-up message in a chat session."""
        resp = chat_session.send_message(message=message)
        return resp.text

    # ── cleanup ───────────────────────────────────────────────────

    def delete_uploaded(self, path: str):
        file_obj = self._uploaded_files.pop(path, None)
        if file_obj:
            try:
                self.client.files.delete(name=file_obj.name)
                logger.info(f"Deleted: {file_obj.name}")
            except Exception as e:
                logger.warning(f"Delete failed: {e}")

    def cleanup_all(self):
        for p in list(self._uploaded_files):
            self.delete_uploaded(p)

    # ── internal ──────────────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """Extract the first JSON object/array from LLM output."""
        m = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
        candidate = m.group(1).strip() if m else text.strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        for o, c in [("{", "}"), ("[", "]")]:
            s, e = text.find(o), text.rfind(c)
            if s != -1 and e > s:
                try:
                    return json.loads(text[s : e + 1])
                except json.JSONDecodeError:
                    continue

        logger.warning("JSON extraction failed — wrapping raw text")
        return {"raw_response": text}


def create_gemini_client(api_key: str) -> GeminiClient:
    return GeminiClient(api_key)
