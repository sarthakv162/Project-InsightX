"""Base agent class."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging


class BaseAgent(ABC):
    """Base class for all InsightX agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"insightx.{name}")

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic.

        Args:
            state: Full LangGraph state dict.

        Returns:
            Partial state update dict (LangGraph merges into state).
        """
        ...

    def log(self, level: str, message: str):
        """Log with agent name prefix."""
        getattr(self.logger, level.lower(), self.logger.info)(
            f"[{self.name}] {message}"
        )
