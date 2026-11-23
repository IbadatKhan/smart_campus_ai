"""
Module: core.models
Description: Data Transfer Objects (DTOs) and data schemas for Smart Campus AI.
Contains pure data structures with zero business logic.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class UniversalRequest:
    """Raw user request captured from the CLI presentation layer."""
    request_id: str = ""
    name: str = ""
    role: str = "student"  # "student", "instructor", "staff"
    request_type: str = "Full_Service_Request"
    # "Navigation_Only", "Eligibility_Check", "Booking_or_Scheduling",
    # "Urgent_Service_Request", "Full_Service_Request"
    category: str = "AI_Lab_Support"
    # "AI_Lab_Support", "Viva_Scheduling", "Access_Request", "Maintenance", "Emergency_Help"
    current_location: str = "Hostel"
    destination: str = "AI_Lab"
    preferred_slot: Optional[int] = 2
    severity: int = 5  # 1..10
    time_sensitivity: int = 5  # 1..10
    crowd_level: int = 5  # 1..10
    group_id: str = ""
    query: str = ""
    eligibility_claim: bool = True
    description_note: str = ""


@dataclass
class PreprocessedRequest:
    """Normalized request containing the extracted 7-dimensional numeric feature vector."""
    raw: UniversalRequest
    request_type: str
    feature_vector: List[float] = field(default_factory=list)
    is_valid: bool = True
    error_message: Optional[str] = None


@dataclass
class PriorityResult:
    """Machine learning priority and urgency classification result."""
    binary_priority: str = "not_urgent"  # "urgent", "not_urgent"
    final_priority: str = "normal"  # "low", "normal", "high", "urgent"
    confidence: float = 0.0  # 0.0 .. 1.0


@dataclass
class LogicResult:
    """Symbolic reasoning and authorization deduction result."""
    allowed: bool = False
    explanation: str = ""
    deduction_trace: List[str] = field(default_factory=list)


@dataclass
class CSPResult:
    """Constraint satisfaction room and timetable assignment result."""
    success: bool = False
    assigned_room: str = ""
    assigned_slot: Optional[int] = None
    destination: str = ""
    notes: str = ""
    timetable: Dict[str, int] = field(default_factory=dict)


@dataclass
class RouteResult:
    """Spatial pathfinding search result carrying navigation metrics."""
    algorithm_used: str = "A*"
    path: List[str] = field(default_factory=list)
    total_cost: float = 0.0
    steps: int = 0
    nodes_expanded: int = 0
    execution_time_ms: float = 0.0


@dataclass
class FinalResponse:
    """Unified system decision response returned to the presentation layer."""
    request_id: str = ""
    decision: str = "pending"  # "accepted", "rejected"
    priority: Optional[PriorityResult] = None
    eligibility: Optional[LogicResult] = None
    assignment: Optional[CSPResult] = None
    route: Optional[RouteResult] = None
    message: str = ""
