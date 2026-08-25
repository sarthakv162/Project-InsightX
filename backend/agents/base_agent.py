"""Base agent class with timeout and retry support."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio
import logging

from config.settings import settings


class BaseAgent(ABC):
    """Base class for all InsightX agents.

    Provides:
      - Configurable per-call timeout (``AGENT_TIMEOUT`` from settings)
      - Automatic retry with exponential back-off (``MAX_RETRIES``)
      - Structured logging with agent name prefix
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"insightx.{name}")

    @abstractmethod
    async def _execute_impl(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Subclass-specific logic.  Override this instead of ``execute()``.

        Args:
            state: Full LangGraph state dict.

        Returns:
            Partial state update dict (LangGraph merges into state).
        """
        ...

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent logic with timeout and retry guards.

        Respects ``settings.AGENT_TIMEOUT`` (seconds) and
        ``settings.MAX_RETRIES``.  On each failure the back-off doubles
        starting from 2 s.
        """
        timeout = settings.AGENT_TIMEOUT
        max_retries = settings.MAX_RETRIES
        last_exc: Exception | None = None

        for attempt in range(1, max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    self._execute_impl(state),
                    timeout=timeout,
                )
                return result
            except asyncio.TimeoutError:
                self.log(
                    "warning",
                    f"Timed out after {timeout}s (attempt {attempt}/{max_retries})",
                )
                last_exc = TimeoutError(
                    f"{self.name} timed out after {timeout}s"
                )
            except Exception as exc:
                self.log(
                    "warning",
                    f"Error on attempt {attempt}/{max_retries}: {exc}",
                )
                last_exc = exc

            if attempt < max_retries:
                backoff = 2 ** attempt  # 2, 4, 8 …
                self.log("info", f"Retrying in {backoff}s …")
                await asyncio.sleep(backoff)

        self.log("error", f"All {max_retries} attempts failed")
        raise last_exc  # type: ignore[misc]

    def log(self, level: str, message: str):
        """Log with agent name prefix."""
        getattr(self.logger, level.lower(), self.logger.info)(
            f"[{self.name}] {message}"
        )
