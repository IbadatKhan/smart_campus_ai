"""
Module: core.core_facade
Description: MASTER FACADE 1 (CoreFacade).
Central orchestrator sitting at Layer 1 <-> Layer 2 boundary (identical to BLLFacade in SCD).
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
    Single point of contact for the Presentation Layer (CLI).
    Coordinates preprocessing, pipeline filtering, and delegates to IAIEngineFacade (Facade 2).
    """

    def __init__(self, router: RequestRouter, ai_facade: IAIEngineFacade) -> None:
        self._router = router
        self._ai = ai_facade

    def execute(self, raw_req: UniversalRequest) -> FinalResponse:
        """
        Executes request through active filter chains with fail-fast gatekeeper logic.
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
        success_msg = self._build_success_message(raw_req, csp_res, route_res)
        return FinalResponse(
            request_id=raw_req.request_id,
            decision="accepted",
            priority=priority_res,
            eligibility=logic_res,
            assignment=csp_res,
            route=route_res,
            message=success_msg
        )

    def run_navigation_benchmark(self, start: str, goal: str):
        """Runs the 9-algorithm benchmark suite through the AI facade."""
        return self._ai.run_benchmark(start, goal)

    def _build_success_message(self, req: UniversalRequest, csp: Optional[CSPResult], route: Optional[RouteResult]) -> str:
        parts = [f"Request '{req.request_id}' successfully processed."]
        if csp and csp.assigned_room:
            parts.append(f"Assigned {csp.assigned_room} at slot {csp.assigned_slot}.")
        if route and route.path:
            parts.append(f"Optimal route: {' -> '.join(route.path)} (Cost: {route.total_cost:.1f}).")
        return " ".join(parts)
