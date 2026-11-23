"""
Module: core.contracts
Description: Abstract Base Classes (ABCs) defining Hexagonal Ports and system contracts.
High-level orchestrators depend strictly on these abstract ports, never on concrete algorithms.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from core.models import RouteResult, PriorityResult, LogicResult, CSPResult


class IRouteFinder(ABC):
    """Abstract Port for spatial pathfinding and campus navigation."""

    @abstractmethod
    def compute_route(self, start_node: str, goal_node: str, graph_type: str = "weighted") -> RouteResult:
        """Computes optimal route between start and goal landmarks."""
        pass

    @abstractmethod
    def run_benchmark(self, start_node: str, goal_node: str) -> Dict[str, RouteResult]:
        """Executes curriculum search algorithms and returns comparative metrics."""
        pass


class IPriorityClassifier(ABC):
    """Abstract Port for machine learning urgency and priority estimation."""

    @abstractmethod
    def classify_binary_urgency(self, feature_vector: List[float]) -> str:
        """Evaluates 7-D vector via Perceptron returning 'urgent' or 'not_urgent'."""
        pass

    @abstractmethod
    def classify_multiclass_priority(self, feature_vector: List[float]) -> PriorityResult:
        """Evaluates 7-D vector via MLP returning operational priority and confidence."""
        pass


class ILogicVerifier(ABC):
    """Abstract Port for symbolic logic reasoning and security gatekeeper checks."""

    @abstractmethod
    def verify_request_eligibility(self, user_name: str, role: str, category: str) -> LogicResult:
        """Verifies if user satisfies course prerequisites and role permissions."""
        pass

    @abstractmethod
    def query_fact(self, fol_query_string: str) -> LogicResult:
        """Evaluates arbitrary FOL query string via forward chaining."""
        pass


class IScheduler(ABC):
    """Abstract Port for CSP resource and timetable allocation."""

    @abstractmethod
    def schedule_service(self, request_id: str, preferred_slot: Optional[int], priority_level: str) -> CSPResult:
        """Assigns conflict-free room and time slot for a service request."""
        pass

    @abstractmethod
    def solve_group_timetable(self, groups: List[str], domains: Dict[str, List[int]]) -> CSPResult:
        """Solves the 6-group examination viva scheduling CSP problem."""
        pass


class IAIEngineFacade(IRouteFinder, IPriorityClassifier, ILogicVerifier, IScheduler):
    """
    Unified Subsystem Facade Interface (Master Facade 2 Port).
    Inherits all 4 ports above with zero duplicate method signatures,
    mirroring IDALFacade in SCD.
    """
    pass
