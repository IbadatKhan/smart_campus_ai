"""
Module: ai_engines.engine_facade
Description: MASTER FACADE 2 (AIEngineFacade).
Sits at Layer 2 <-> Layer 3 boundary over computational AI subsystems.
Provides a single unified interface over all 4 AI engines with Day-1 stub fallbacks.
"""

from typing import List, Dict, Optional
from core.contracts import (
    IAIEngineFacade,
    IRouteFinder,
    IPriorityClassifier,
    ILogicVerifier,
    IScheduler
)
from core.models import RouteResult, PriorityResult, LogicResult, CSPResult
from ai_engines.navigation.search_engine import SearchEngine
from ai_engines.reasoning.logic_kb import LogicKBGatekeeper
from ai_engines.reasoning.csp_scheduler import CSPScheduler


# =====================================================================
# Day-1 In-Memory Stubs (Zero Blocker Guarantee for Parallel Development)
# =====================================================================

class _StubRouteFinder(IRouteFinder):
    def compute_route(self, start_node: str, goal_node: str, graph_type: str = "weighted") -> RouteResult:
        return RouteResult(
            algorithm_used="A* (Stub)",
            path=[start_node, goal_node] if start_node != goal_node else [start_node],
            total_cost=4.0,
            steps=1,
            nodes_expanded=2,
            execution_time_ms=0.1
        )

    def run_benchmark(self, start_node: str, goal_node: str) -> Dict[str, RouteResult]:
        return {
            "A*": self.compute_route(start_node, goal_node),
            "BFS": self.compute_route(start_node, goal_node)
        }


class _StubPriorityClassifier(IPriorityClassifier):
    def classify_binary_urgency(self, feature_vector: List[float]) -> str:
        severity = feature_vector[2] if len(feature_vector) > 2 else 5.0
        return "urgent" if severity >= 8.0 else "not_urgent"

    def classify_multiclass_priority(self, feature_vector: List[float]) -> PriorityResult:
        severity = feature_vector[2] if len(feature_vector) > 2 else 5.0
        if severity >= 8.0:
            return PriorityResult(binary_priority="urgent", final_priority="urgent", confidence=0.92)
        elif severity >= 6.0:
            return PriorityResult(binary_priority="urgent", final_priority="high", confidence=0.85)
        elif severity >= 4.0:
            return PriorityResult(binary_priority="not_urgent", final_priority="normal", confidence=0.78)
        else:
            return PriorityResult(binary_priority="not_urgent", final_priority="low", confidence=0.95)


class _StubLogicVerifier(ILogicVerifier):
    def verify_request_eligibility(self, user_name: str, role: str, category: str) -> LogicResult:
        # Default policy: students and instructors are allowed; unknown denied
        role_clean = role.strip().lower()
        if role_clean in ["student", "instructor", "staff"]:
            return LogicResult(
                allowed=True,
                explanation=f"User '{user_name}' ({role}) is authorized for category '{category}'."
            )
        return LogicResult(
            allowed=False,
            explanation=f"Role '{role}' is not authorized for '{category}'."
        )

    def query_fact(self, fol_query_string: str) -> LogicResult:
        return LogicResult(allowed=True, explanation=f"Query '{fol_query_string}' holds true.")


class _StubScheduler(IScheduler):
    def schedule_service(self, request_id: str, preferred_slot: Optional[int], priority_level: str) -> CSPResult:
        slot = preferred_slot if preferred_slot is not None and preferred_slot > 0 else 1
        return CSPResult(
            success=True,
            assigned_room="AI_Lab",
            assigned_slot=slot,
            destination="AI_Lab",
            notes=f"Assigned slot {slot} in AI_Lab for priority '{priority_level}'."
        )

    def solve_group_timetable(self, groups: List[str], domains: Dict[str, List[int]]) -> CSPResult:
        assigned = {g: (i + 1) for i, g in enumerate(groups)}
        return CSPResult(
            success=True,
            assigned_room="Seminar_Room",
            assigned_slot=1,
            notes="6-group conflict-free timetable solved successfully.",
            timetable=assigned
        )


# =====================================================================
# Master Facade 2: AIEngineFacade
# =====================================================================

class AIEngineFacade(IAIEngineFacade):
    """
    Master Facade 2:
    The single gatekeeper for Layer 3 computational AI subsystems.
    Injects the 4 AI engine implementations and delegates calls to them.
    Falls back gracefully to built-in stubs if an engine is not yet supplied.
    """

    def __init__(
        self,
        route_finder: Optional[IRouteFinder] = None,
        priority_classifier: Optional[IPriorityClassifier] = None,
        logic_verifier: Optional[ILogicVerifier] = None,
        scheduler: Optional[IScheduler] = None
    ) -> None:
        self._nav: IRouteFinder = route_finder or SearchEngine()
        self._ann: IPriorityClassifier = priority_classifier or _StubPriorityClassifier()
        self._logic: ILogicVerifier = logic_verifier or LogicKBGatekeeper()
        self._csp: IScheduler = scheduler or CSPScheduler()

    # --- Routing Delegations ---
    def compute_route(self, start_node: str, goal_node: str, graph_type: str = "weighted") -> RouteResult:
        return self._nav.compute_route(start_node, goal_node, graph_type)

    def run_benchmark(self, start_node: str, goal_node: str) -> Dict[str, RouteResult]:
        return self._nav.run_benchmark(start_node, goal_node)

    # --- Neural ANN Delegations ---
    def classify_binary_urgency(self, feature_vector: List[float]) -> str:
        return self._ann.classify_binary_urgency(feature_vector)

    def classify_multiclass_priority(self, feature_vector: List[float]) -> PriorityResult:
        return self._ann.classify_multiclass_priority(feature_vector)

    # --- Symbolic Logic Delegations ---
    def verify_request_eligibility(self, user_name: str, role: str, category: str) -> LogicResult:
        return self._logic.verify_request_eligibility(user_name, role, category)

    def query_fact(self, fol_query_string: str) -> LogicResult:
        return self._logic.query_fact(fol_query_string)

    # --- CSP Scheduler Delegations ---
    def schedule_service(self, request_id: str, preferred_slot: Optional[int], priority_level: str) -> CSPResult:
        return self._csp.schedule_service(request_id, preferred_slot, priority_level)

    def solve_group_timetable(self, groups: List[str], domains: Dict[str, List[int]]) -> CSPResult:
        return self._csp.solve_group_timetable(groups, domains)
