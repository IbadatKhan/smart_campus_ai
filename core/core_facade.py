"""
Module: core.core_facade
Description: MASTER FACADE 1 (CoreFacade).
Central orchestrator sitting at Layer 1 <-> Layer 2 boundary.
Coordinates the 5 Canonical Pipelines with fail-fast early exit rejections.
"""

from typing import Optional
from core.contracts import IAIEngineFacade
from core.router import RequestRouter
from core.models import (
    UniversalRequest,
    FinalResponse,
    PriorityResult,
    LogicResult,
    CSPResult,
    RouteResult
)


class CoreFacade:
    """
    Master Facade 1:
    Single point of contact for the Presentation Layer (CLI & GUI).
    Coordinates preprocessing, pipeline filtering, and delegates to IAIEngineFacade (Facade 2).
    """

    def __init__(self, router: RequestRouter, ai_facade: IAIEngineFacade) -> None:
        """
        Initializes CoreFacade with the request router and AI engine facade.
        """
        self._router = router
        self._ai = ai_facade

    def execute(self, raw_req: UniversalRequest) -> FinalResponse:
        """
        Executes a user request through active filter chains with fail-fast gatekeeper logic.
        Validates input, runs required AI modules, and returns an aggregated FinalResponse.
        """
        # Stage 1: Preprocessing & Validation
        preprocessed = self._router.process(raw_req)
        if not preprocessed.is_valid:
            return FinalResponse(
                request_id=raw_req.request_id,
                decision="rejected",
                message=preprocessed.error_message or "Validation failed."
            )

        filters = self._router.get_active_filters(preprocessed.request_type)
        priority_res: Optional[PriorityResult] = None
        logic_res: Optional[LogicResult] = None
        csp_res: Optional[CSPResult] = None
        route_res: Optional[RouteResult] = None

        # Stage 2: ANN Priority Estimation (if active)
        if "ANN" in filters:
            priority_res = self._ai.classify_multiclass_priority(preprocessed.feature_vector)

        # Stage 3: Symbolic Logic Gatekeeper (if active)
        if "LOGIC" in filters:
            # If request is an Eligibility_Check with a formal logic query string
            if preprocessed.request_type == "Eligibility_Check" and raw_req.query and raw_req.query.strip():
                logic_res = self._ai.query_fact(raw_req.query.strip())
            else:
                logic_res = self._ai.verify_request_eligibility(
                    user_name=raw_req.name,
                    role=raw_req.role,
                    category=raw_req.category
                )

            # Circuit Breaker: Fail-fast if gatekeeper rejects
            if not logic_res.allowed:
                return FinalResponse(
                    request_id=raw_req.request_id,
                    decision="rejected",
                    priority=priority_res,
                    eligibility=logic_res,
                    message=f"Access Denied: {logic_res.explanation}"
                )

        # Stage 4: CSP Resource & Timetable Scheduling (if active)
        if "CSP" in filters:
            prio_level = priority_res.final_priority if priority_res else "normal"
            csp_res = self._ai.schedule_service(
                request_id=raw_req.request_id,
                preferred_slot=raw_req.preferred_slot,
                priority_level=prio_level
            )
            # Fail-fast if no conflict-free slot exists
            if not csp_res.success:
                return FinalResponse(
                    request_id=raw_req.request_id,
                    decision="rejected",
                    priority=priority_res,
                    eligibility=logic_res,
                    assignment=csp_res,
                    message=f"Scheduling Conflict: {csp_res.notes}"
                )

        # Stage 5: Spatial Graph Navigation (if active)
        if "SEARCH" in filters:
            start_point = raw_req.current_location or "Main_Gate"
            # Target room from CSP assignment, or user destination
            target_point = (csp_res.assigned_room if csp_res and csp_res.assigned_room
                            else raw_req.destination or "AI_Lab")

            route_res = self._ai.compute_route(start_point, target_point)
            if not route_res.path:
                return FinalResponse(
                    request_id=raw_req.request_id,
                    decision="rejected",
                    priority=priority_res,
                    eligibility=logic_res,
                    assignment=csp_res,
                    route=route_res,
                    message=f"Navigation Error: No viable path from '{start_point}' to '{target_point}'."
                )

        # Build Accepted Unified Response
        success_msg = self._build_success_message(raw_req, csp_res, route_res, logic_res)
        return FinalResponse(
            request_id=raw_req.request_id,
            decision="accepted",
            priority=priority_res,
            eligibility=logic_res,
            assignment=csp_res,
            route=route_res,
            message=success_msg
        )

    def compute_route(self, start: str, goal: str, graph_type: str = "weighted") -> RouteResult:
        """
        Directly computes the optimal navigation route between two landmarks.
        """
        return self._ai.compute_route(start, goal, graph_type)

    def run_navigation_benchmark(self, start: str, goal: str):
        """
        Runs the 9-algorithm benchmark suite through the AI facade.
        Returns comparative performance metrics for curriculum search algorithms.
        """
        return self._ai.run_benchmark(start, goal)

    def _build_success_message(
        self,
        req: UniversalRequest,
        csp: Optional[CSPResult],
        route: Optional[RouteResult],
        logic: Optional[LogicResult] = None
    ) -> str:
        """
        Constructs a human-readable summary message tailored to the processed pipeline.
        """
        if req.request_type == "Eligibility_Check" and logic:
            return f"Eligibility query resolved: {logic.explanation}"

        parts = [f"Request '{req.request_id}' successfully processed."]
        if csp and csp.assigned_room:
            parts.append(f"Assigned {csp.assigned_room} at slot {csp.assigned_slot}.")
        if route and route.path:
            parts.append(f"Optimal route: {' -> '.join(route.path)} (Cost: {route.total_cost:.1f}).")
        return " ".join(parts)
