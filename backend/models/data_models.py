"""Data models and types for InsightX"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, TypedDict
from enum import Enum


class SportType(str, Enum):
    """Supported sports"""
    CRICKET = "cricket"
    TENNIS = "tennis"
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    BADMINTON = "badminton"
    VOLLEYBALL = "volleyball"
    UNKNOWN = "unknown"


class QueryType(str, Enum):
    """Types of user queries"""
    ERROR_ANALYSIS = "error_analysis"  # What went wrong?
    COMPARISON = "comparison"  # Compare two videos
    LEARNING_PLAN = "learning_plan"  # How to learn this?
    OPPONENT_STRATEGY = "opponent_strategy"  # How could opponent have won?
    EVENT_LOCATION = "event_location"  # Take me to the instance
    GENERAL_ANALYSIS = "general_analysis"  # General feedback


@dataclass
class VideoMetadata:
    """Metadata about a video"""
    video_path: str
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    sport: SportType = SportType.UNKNOWN
    player_name: Optional[str] = None
    source: str = "local"  # "local", "youtube", etc.
    cached: bool = False
    cache_id: Optional[str] = None


@dataclass
class Timestamp:
    """Represents a time in a video"""
    start_seconds: float
    end_seconds: float
    
    @property
    def duration(self) -> float:
        return self.end_seconds - self.start_seconds


@dataclass
class KeyEvent:
    """Represents a critical event in the video"""
    event_type: str  # e.g., "serve", "volley", "shot_loss", "recovery"
    timestamp: Timestamp
    confidence: float  # 0-1
    description: str
    visual_indicators: List[str] = field(default_factory=list)


@dataclass
class BiomechanicalAnalysis:
    """Results from kinematic comparison"""
    dimension: str  # e.g., "knee_angle", "arm_position", "weight_distribution"
    reference_value: Optional[float]  # e.g., angle in degrees
    user_value: Optional[float]
    delta: Optional[float]  # Difference
    confidence: float  # 0-1
    description: str
    recommendation: Optional[str] = None


@dataclass
class TacticalInsight:
    """Tactical analysis result"""
    insight_type: str  # e.g., "positioning_error", "timing_mistake", "strategy_mismatch"
    confidence: float  # 0-1
    description: str
    opposing_strategy: Optional[str] = None
    why_it_failed: str = ""
    correction_strategy: Optional[str] = None


@dataclass
class CoachingDrill:
    """A single training drill"""
    name: str
    duration_minutes: int
    description: str
    steps: List[str]
    repetitions: int
    focus_area: str
    difficulty_level: str  # "beginner", "intermediate", "advanced"


@dataclass
class LearningPlan:
    """Personalized learning plan"""
    title: str
    target_skill: str
    duration_weeks: int
    weekly_focus: List[str]
    drills: List[CoachingDrill]
    milestones: List[str]
    progression: str


@dataclass
class AgentState:
    """Shared state across agents in the workflow"""
    user_query: str
    query_type: QueryType
    videos: List[VideoMetadata]
    sport: SportType
    
    # Results from different agents
    key_events: List[KeyEvent] = field(default_factory=list)
    biomechanical_analysis: List[BiomechanicalAnalysis] = field(default_factory=list)
    tactical_insights: List[TacticalInsight] = field(default_factory=list)
    coaching_plan: Optional[LearningPlan] = None
    
    # Intermediate results
    scouter_results: Dict[str, Any] = field(default_factory=dict)
    analyst_results: Dict[str, Any] = field(default_factory=dict)
    strategist_results: Dict[str, Any] = field(default_factory=dict)
    coach_results: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    clarification_required: bool = False
    clarification_questions: List[str] = field(default_factory=list)
    confidence_level: float = 1.0


@dataclass
class AnalysisResponse:
    """Final response from the InsightX system"""
    success: bool
    query: str
    analysis: Dict[str, Any]
    key_events: List[KeyEvent]
    biomechanical_findings: List[BiomechanicalAnalysis]
    tactical_findings: List[TacticalInsight]
    coaching_recommendations: Optional[LearningPlan]
    confidence_score: float
    processing_time_seconds: float


# ── LangGraph State (TypedDict) ────────────────────────────────

class GraphState(TypedDict, total=False):
    """
    LangGraph-compatible state — a plain dict under the hood.

    All values are JSON-serialisable primitives / dicts / lists so
    LangGraph can merge partial updates from each agent node.
    """

    # Input
    user_query: str
    query_type: str               # QueryType enum .value as string
    video_sources: List[str]      # Local file paths *or* YouTube URLs
    sport: str                    # SportType enum .value as string

    # Agent structured outputs (serialisable dicts)
    key_events: List[Dict[str, Any]]
    biomechanical_analysis: List[Dict[str, Any]]
    tactical_insights: List[Dict[str, Any]]
    coaching_plan: Optional[Dict[str, Any]]

    # Agent natural-language summaries
    scouter_summary: str
    analyst_summary: str
    strategist_summary: str
    coach_summary: str

    # Final synthesised response
    final_response: str

    # Chat / control
    chat_history: List[Dict[str, str]]
    clarification_required: bool
    clarification_questions: List[str]
    confidence_level: float

