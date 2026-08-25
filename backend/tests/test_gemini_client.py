"""Tests for GeminiClient — no API calls required.

Tests JSON extraction, YouTube URL detection, and client initialization.
"""

import pytest
from utils.gemini_client import GeminiClient


class TestYouTubeUrlDetection:
    """Test YouTube URL regex matching."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=abc123",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/abc123",
            "youtube.com/watch?v=test-123",
        ],
    )
    def test_valid_youtube_urls(self, url):
        assert GeminiClient.is_youtube_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "/home/user/video.mp4",
            "https://vimeo.com/12345",
            "not_a_url",
            "",
            "https://google.com/watch?v=abc",
        ],
    )
    def test_invalid_youtube_urls(self, url):
        assert GeminiClient.is_youtube_url(url) is False


class TestJsonExtraction:
    """Test the _extract_json static method."""

    def test_extract_fenced_json(self):
        text = 'Some text\n```json\n{"key": "value"}\n```\nMore text'
        result = GeminiClient._extract_json(text)
        assert result == {"key": "value"}

    def test_extract_unfenced_json(self):
        text = 'Here is the result: {"events": [1, 2, 3]}'
        result = GeminiClient._extract_json(text)
        assert result == {"events": [1, 2, 3]}

    def test_extract_json_array(self):
        text = '[{"a": 1}, {"b": 2}]'
        result = GeminiClient._extract_json(text)
        assert result == [{"a": 1}, {"b": 2}]

    def test_extract_nested_json(self):
        text = '```\n{"analyses": [{"dim": "knee", "conf": 0.9}]}\n```'
        result = GeminiClient._extract_json(text)
        assert result["analyses"][0]["dim"] == "knee"

    def test_fallback_on_invalid_json(self):
        text = "This is not JSON at all"
        result = GeminiClient._extract_json(text)
        assert "raw_response" in result
        assert result["raw_response"] == text

    def test_json_with_surrounding_text(self):
        text = """
        I analysed the video and here are the results:
        
        {"events": [{"type": "serve", "time": 3.5}], "summary": "Good match"}
        
        Hope this helps!
        """
        result = GeminiClient._extract_json(text)
        assert "events" in result
        assert result["events"][0]["type"] == "serve"
