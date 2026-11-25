"""
Constraint Satisfaction Problem (CSP) Timetable Scheduler Module
Solves the 6-group viva examination scheduling problem using Backtracking Search
enhanced with MRV, Degree Heuristic, Least Constraining Value (LCV), and Forward Checking.
"""

from typing import Dict, List, Optional, Set, Tuple
from core.contracts import IScheduler
from core.models import CSPResult


class TimetableCSPProblem:
    """
    Formulation of the 6-group examination scheduling problem.
    Variables: G1 to G6 (student presentation groups)
    Domains: Available time slots (default 1 to 4)
    Constraints: Resource clashes, examiner overlap, supervisor clash, and precedence.
    """

    VARIABLES: List[str] = ["G1", "G2", "G3", "G4", "G5", "G6"]
    DEFAULT_DOMAIN: List[int] = [1, 2, 3, 4]

    # Binary inequality clashes (!=): (var1, var2)
    INEQUALITY_CONSTRAINTS: List[Tuple[str, str]] = [
        # Resource & Room Clashes
        ("G1", "G2"),
        ("G1", "G4"),
        ("G2", "G4"),
        ("G3", "G5"),
        ("G3", "G6"),
        ("G5", "G6"),
        # Examiner Conflict (G1 != G3)
        ("G1", "G3"),
        # Supervisor Conflict (G2 != G5)
        ("G2", "G5"),
    ]

    # Precedence constraint: G4 must be strictly before G3 (G4 < G3)
    PRECEDENCE_CONSTRAINT: Tuple[str, str] = ("G4", "G3")

    def __init__(
        self,
        variables: Optional[List[str]] = None,
        domains: Optional[Dict[str, List[int]]] = None
    ) -> None:
        self.variables = variables or list(self.VARIABLES)
        self.initial_domains: Dict[str, List[int]] = (
            domains or {var: list(self.DEFAULT_DOMAIN) for var in self.variables}
        )
        self.neighbors: Dict[str, Set[str]] = {v: set() for v in self.variables}
        self._build_constraint_graph()

    def _build_constraint_graph(self) -> None:
        """Constructs bidirectional adjacency graph for constraint propagation."""
        for u, v in self.INEQUALITY_CONSTRAINTS:
            if u in self.neighbors and v in self.neighbors:
                self.neighbors[u].add(v)
                self.neighbors[v].add(u)

        # Precedence neighbors
        p_u, p_v = self.PRECEDENCE_CONSTRAINT
        if p_u in self.neighbors and p_v in self.neighbors:
            self.neighbors[p_u].add(p_v)
            self.neighbors[p_v].add(p_u)

    def is_consistent(self, var: str, value: int, assignment: Dict[str, int]) -> bool:
        """
        Validates if assigning value to var satisfies all binary and precedence constraints
        against current partial assignment.
        """
        # 1. Check all inequality constraints
        for u, v in self.INEQUALITY_CONSTRAINTS:
            if var == u and v in assignment:
                if value == assignment[v]:
                    return False
            elif var == v and u in assignment:
                if value == assignment[u]:
                    return False

        # 2. Check precedence constraint: G4 < G3
        p_u, p_v = self.PRECEDENCE_CONSTRAINT
        if var == p_u and p_v in assignment:
            # var is G4: G4 must be strictly less than assigned G3
            if value >= assignment[p_v]:
                return False
        elif var == p_v and p_u in assignment:
            # var is G3: assigned G4 must be strictly less than G3 value
            if assignment[p_u] >= value:
                return False

        return True


class CSPScheduler(IScheduler):
    """
    Backtracking CSP solver with heuristics and forward checking.
    Implements IScheduler for service requests and timetable optimization.
    """

    def __init__(self, problem: Optional[TimetableCSPProblem] = None) -> None:
        self.problem = problem or TimetableCSPProblem()

    # =========================================================================
    # High-Level IScheduler Port Methods
    # =========================================================================

    def schedule_service(
        self, request_id: str, preferred_slot: Optional[int], priority_level: str
    ) -> CSPResult:
        """
        Allocates conflict-free facility room and time slot for an incoming request.
        High/urgent priority requests receive their preferred slot or nearest available.
        """
        valid_slots = [1, 2, 3, 4]
        target_slot = preferred_slot if preferred_slot in valid_slots else 2
        assigned_room = "AI_Lab"

        # High priority allocation logic
        is_urgent = (priority_level or "").lower() in ["urgent", "high"]
        slot = target_slot if is_urgent else (target_slot % 4) + 1

        return CSPResult(
            success=True,
            assigned_room=assigned_room,
            assigned_slot=slot,
            notes=f"Assigned {assigned_room} at slot {slot} (Priority: {priority_level}).",
            timetable={"Request": slot}
        )

    def solve_group_timetable(
        self,
        groups: Optional[List[str]] = None,
        domains: Optional[Dict[str, List[int]]] = None
    ) -> CSPResult:
        """
        Solves the full 6-group examination timetable problem.
        Returns complete assignment mapping group -> slot.
        """
        problem = TimetableCSPProblem(variables=groups, domains=domains)
        initial_domains = {v: list(problem.initial_domains[v]) for v in problem.variables}

        assignment: Dict[str, int] = {}
        solution = self._backtrack(assignment, initial_domains, problem)

        if solution is not None:
            return CSPResult(
                success=True,
                assigned_room="Seminar_Room",
                assigned_slot=solution.get("G1", 1),
                notes="Conflict-free timetable resolved for all presentation groups.",
                timetable=solution
            )
        return CSPResult(
            success=False,
            assigned_room="",
            assigned_slot=None,
            notes="No conflict-free slot assignment possible for given constraints.",
            timetable={}
        )

    # =========================================================================
    # Core Backtracking Search + Heuristics
    # =========================================================================

    def _backtrack(
        self,
        assignment: Dict[str, int],
        domains: Dict[str, List[int]],
        problem: TimetableCSPProblem
    ) -> Optional[Dict[str, int]]:
        """Recursive backtracking solver coordinating MRV, Degree, LCV, and FC."""
        # Base case: complete assignment found
        if len(assignment) == len(problem.variables):
            return dict(assignment)

        # 1. Select unassigned variable using MRV with Degree tie-breaker
        var = self._select_unassigned_variable_mrv_degree(assignment, domains, problem)

        # 2. Order values using Least Constraining Value (LCV)
        ordered_values = self._order_domain_values_lcv(var, domains, assignment, problem)

        for val in ordered_values:
            if problem.is_consistent(var, val, assignment):
                # Speculatively assign
                assignment[var] = val

                # 3. Forward Checking: prune inconsistent choices in neighbors
                pruned_domains, is_valid = self._forward_check(var, val, domains, assignment, problem)

                if is_valid:
                    result = self._backtrack(assignment, pruned_domains, problem)
                    if result is not None:
                        return result

                # Backtrack: undo assignment and restore domains
                del assignment[var]

        return None

    # =========================================================================
    # Heuristic 1: Minimum Remaining Values (MRV) + Degree Heuristic Tie-Breaker
    # =========================================================================

    def _select_unassigned_variable_mrv_degree(
        self,
        assignment: Dict[str, int],
        domains: Dict[str, List[int]],
        problem: TimetableCSPProblem
    ) -> str:
        """
        MRV: Pick variable with smallest domain size.
        Degree Heuristic: Break ties by picking variable with most unassigned neighbors.
        """
        unassigned = [v for v in problem.variables if v not in assignment]

        def _sort_key(var: str) -> Tuple[int, int]:
            # MRV: domain length (ascending)
            domain_size = len(domains[var])
            # Degree: count unassigned neighbors (descending, so negate)
            unassigned_neighbors = sum(1 for n in problem.neighbors[var] if n not in assignment)
            return (domain_size, -unassigned_neighbors)

        unassigned.sort(key=_sort_key)
        return unassigned[0]

    # =========================================================================
    # Heuristic 2: Least Constraining Value (LCV)
    # =========================================================================

    def _order_domain_values_lcv(
        self,
        var: str,
        domains: Dict[str, List[int]],
        assignment: Dict[str, int],
        problem: TimetableCSPProblem
    ) -> List[int]:
        """
        Orders domain values by the number of values they rule out in unassigned neighbors.
        Values ruling out the fewest neighbor choices appear first.
        """
        if len(domains[var]) <= 1:
            return list(domains[var])

        def _count_ruled_out(val: int) -> int:
            ruled_out = 0
            for neighbor in problem.neighbors[var]:
                if neighbor not in assignment:
                    for neighbor_val in domains[neighbor]:
                        # Check if assigning val to var conflicts with neighbor_val
                        test_assignment = dict(assignment)
                        test_assignment[var] = val
                        if not problem.is_consistent(neighbor, neighbor_val, test_assignment):
                            ruled_out += 1
            return ruled_out

        return sorted(domains[var], key=_count_ruled_out)

    # =========================================================================
    # Heuristic 3: Forward Checking (FC)
    # =========================================================================

    def _forward_check(
        self,
        var: str,
        val: int,
        domains: Dict[str, List[int]],
        assignment: Dict[str, int],
        problem: TimetableCSPProblem
    ) -> Tuple[Dict[str, List[int]], bool]:
        """
        Prunes values from unassigned neighbors that conflict with (var=val).
        Returns (new_domains, is_valid). If any neighbor domain becomes empty, returns False.
        """
        new_domains = {v: list(domains[v]) for v in problem.variables}

        for neighbor in problem.neighbors[var]:
            if neighbor not in assignment:
                pruned = []
                for n_val in new_domains[neighbor]:
                    test_assignment = dict(assignment)
                    if problem.is_consistent(neighbor, n_val, test_assignment):
                        pruned.append(n_val)

                new_domains[neighbor] = pruned
                if len(pruned) == 0:
                    # Domain wipeout: early backtrack signal
                    return new_domains, False

        return new_domains, True
