"""
Graph Search Engine Module
Implements classical search strategies over the campus graph topology,
including BFS, DFS, UCS, A* (Euclidean), and a comparative benchmark suite.
"""

import time
import heapq
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from core.contracts import IRouteFinder
from core.models import RouteResult
from ai_engines.navigation.campus_graph import CampusGraph


class SearchNode:
    """
    Search tree node tracking state, parent pointer, and path costs.
    Implements comparison for heapq based on evaluation score f(n).
    """

    def __init__(
        self,
        state: str,
        parent: Optional["SearchNode"] = None,
        path_cost: float = 0.0,
        heuristic_cost: float = 0.0,
        depth: int = 0
    ) -> None:
        self.state = state
        self.parent = parent
        self.path_cost = path_cost
        self.heuristic_cost = heuristic_cost
        self.depth = depth
        self.total_cost = path_cost + heuristic_cost

    def __lt__(self, other: "SearchNode") -> bool:
        # Tie-breaker prioritizes lower heuristic if f(n) values are identical
        if abs(self.total_cost - other.total_cost) < 1e-6:
            return self.heuristic_cost < other.heuristic_cost
        return self.total_cost < other.total_cost

    def reconstruct_path(self) -> List[str]:
        """Backtracks from current node to root to build landmark sequence."""
        path = []
        curr: Optional[SearchNode] = self
        while curr is not None:
            path.append(curr.state)
            curr = curr.parent
        path.reverse()
        return path


class SearchEngine(IRouteFinder):
    """
    Main spatial pathfinding engine implementing IRouteFinder.
    Coordinates graph search strategies and comparative benchmarking.
    """

    def __init__(self, graph: Optional[CampusGraph] = None) -> None:
        self.graph = graph or CampusGraph()

    # =========================================================================
    # High-Level Interface Methods (IRouteFinder)
    # =========================================================================

    def compute_route(
        self, start_node: str, goal_node: str, graph_type: str = "weighted"
    ) -> RouteResult:
        """
        Computes route between landmarks. Uses A* for weighted distance
        and BFS for unweighted minimum-hop navigation.
        """
        if not self.graph.is_valid_node(start_node) or not self.graph.is_valid_node(goal_node):
            return RouteResult(
                algorithm_used="Error",
                path=[],
                total_cost=0.0,
                steps=0,
                nodes_expanded=0
            )

        if start_node == goal_node:
            return RouteResult(
                algorithm_used="Direct",
                path=[start_node],
                total_cost=0.0,
                steps=0,
                nodes_expanded=1
            )

        if graph_type == "unweighted":
            return self.bfs_search(start_node, goal_node)
        return self.astar_search(start_node, goal_node)

    def run_benchmark(self, start_node: str, goal_node: str) -> Dict[str, RouteResult]:
        """
        Executes all 9 curriculum search algorithms between two nodes
        and returns comparative metrics for performance analysis.
        """
        results: Dict[str, RouteResult] = {}
        algorithms = [
            ("Breadth-First Search (BFS)", lambda: self.bfs_search(start_node, goal_node)),
            ("Depth-First Search (DFS)", lambda: self.dfs_search(start_node, goal_node)),
            ("Uniform Cost Search (UCS)", lambda: self.ucs_search(start_node, goal_node)),
            ("Depth-Limited Search (DLS, L=4)", lambda: self.dls_search(start_node, goal_node, limit=4)),
            ("Iterative Deepening Search (IDS)", lambda: self.ids_search(start_node, goal_node, max_depth=8)),
            ("Greedy Best-First Search", lambda: self.greedy_best_first(start_node, goal_node)),
            ("A* Search (Euclidean)", lambda: self.astar_search(start_node, goal_node)),
            ("Recursive Best-First Search (RBFS)", lambda: self.rbfs_search(start_node, goal_node)),
            ("Bidirectional BFS", lambda: self.bidirectional_bfs(start_node, goal_node)),
        ]

        for name, fn in algorithms:
            t0 = time.perf_counter()
            res = fn()
            res.execution_time_ms = round((time.perf_counter() - t0) * 1000, 3)
            results[name] = res

        return results

    # =========================================================================
    # Algorithm 1: Breadth-First Search (BFS)
    # =========================================================================

    def bfs_search(self, start: str, goal: str) -> RouteResult:
        """Explores state space level-by-level; optimal for hop count."""
        frontier = deque([SearchNode(start)])
        explored: Set[str] = {start}
        expanded_count = 0

        while frontier:
            node = frontier.popleft()
            expanded_count += 1

            if node.state == goal:
                path = node.reconstruct_path()
                cost = self._calculate_path_cost(path)
                return RouteResult("BFS", path, cost, len(path) - 1, expanded_count)

            for neighbor, weight in self.graph.get_neighbors(node.state, weighted=True):
                if neighbor not in explored:
                    explored.add(neighbor)
                    frontier.append(SearchNode(neighbor, parent=node, path_cost=node.path_cost + weight))

        return RouteResult("BFS", [], 0.0, 0, expanded_count)

    # =========================================================================
    # Algorithm 2: Depth-First Search (DFS)
    # =========================================================================

    def dfs_search(self, start: str, goal: str) -> RouteResult:
        """Explores deepest branch first using LIFO frontier."""
        frontier = [SearchNode(start)]
        explored: Set[str] = set()
        expanded_count = 0

        while frontier:
            node = frontier.pop()
            if node.state in explored:
                continue
            explored.add(node.state)
            expanded_count += 1

            if node.state == goal:
                path = node.reconstruct_path()
                cost = self._calculate_path_cost(path)
                return RouteResult("DFS", path, cost, len(path) - 1, expanded_count)

            # Reversed for predictable alphabetical neighbor exploration
            for neighbor, weight in reversed(self.graph.get_neighbors(node.state, weighted=True)):
                if neighbor not in explored:
                    frontier.append(SearchNode(neighbor, parent=node, path_cost=node.path_cost + weight))

        return RouteResult("DFS", [], 0.0, 0, expanded_count)

    # =========================================================================
    # Algorithm 3: Uniform Cost Search (UCS / Dijkstra)
    # =========================================================================

    def ucs_search(self, start: str, goal: str) -> RouteResult:
        """Expands lowest path cost g(n) first; optimal for weighted graphs."""
        counter = 0
        frontier: List[Tuple[float, int, SearchNode]] = []
        heapq.heappush(frontier, (0.0, counter, SearchNode(start)))
        best_g: Dict[str, float] = {start: 0.0}
        expanded_count = 0

        while frontier:
            cost, _, node = heapq.heappop(frontier)
            if cost > best_g.get(node.state, float("inf")):
                continue

            expanded_count += 1
            if node.state == goal:
                path = node.reconstruct_path()
                return RouteResult("UCS", path, node.path_cost, len(path) - 1, expanded_count)

            for neighbor, weight in self.graph.get_neighbors(node.state, weighted=True):
                new_cost = node.path_cost + weight
                if new_cost < best_g.get(neighbor, float("inf")):
                    best_g[neighbor] = new_cost
                    counter += 1
                    child = SearchNode(neighbor, parent=node, path_cost=new_cost)
                    heapq.heappush(frontier, (new_cost, counter, child))

        return RouteResult("UCS", [], 0.0, 0, expanded_count)

    # =========================================================================
    # Algorithm 4: A* Search (Euclidean Heuristic)
    # =========================================================================

    def astar_search(self, start: str, goal: str) -> RouteResult:
        """
        Orders frontier by f(n) = g(n) + h(n).
        Admissible Euclidean heuristic guarantees least-cost optimality.
        """
        counter = 0
        initial_h = self.graph.euclidean_heuristic(start, goal)
        start_node = SearchNode(start, path_cost=0.0, heuristic_cost=initial_h)

        frontier: List[Tuple[float, int, SearchNode]] = []
        heapq.heappush(frontier, (start_node.total_cost, counter, start_node))
        best_g: Dict[str, float] = {start: 0.0}
        expanded_count = 0

        while frontier:
            f_val, _, node = heapq.heappop(frontier)
            if node.path_cost > best_g.get(node.state, float("inf")):
                continue

            expanded_count += 1
            if node.state == goal:
                path = node.reconstruct_path()
                return RouteResult("A*", path, node.path_cost, len(path) - 1, expanded_count)

            for neighbor, weight in self.graph.get_neighbors(node.state, weighted=True):
                new_g = node.path_cost + weight
                if new_g < best_g.get(neighbor, float("inf")):
                    best_g[neighbor] = new_g
                    h_val = self.graph.euclidean_heuristic(neighbor, goal)
                    counter += 1
                    child = SearchNode(neighbor, parent=node, path_cost=new_g, heuristic_cost=h_val)
                    heapq.heappush(frontier, (child.total_cost, counter, child))

        return RouteResult("A*", [], 0.0, 0, expanded_count)

    # =========================================================================
    # Algorithm 5: Depth-Limited Search (DLS)
    # =========================================================================

    def dls_search(self, start: str, goal: str, limit: int = 4) -> RouteResult:
        """DFS bounded by an explicit depth cutoff."""
        frontier = [SearchNode(start, depth=0)]
        explored: Set[Tuple[str, int]] = set()
        expanded_count = 0

        while frontier:
            node = frontier.pop()
            state_depth = (node.state, node.depth)
            if state_depth in explored:
                continue
            explored.add(state_depth)
            expanded_count += 1

            if node.state == goal:
                path = node.reconstruct_path()
                cost = self._calculate_path_cost(path)
                return RouteResult("DLS", path, cost, len(path) - 1, expanded_count)

            if node.depth < limit:
                for neighbor, weight in reversed(self.graph.get_neighbors(node.state, weighted=True)):
                    if (neighbor, node.depth + 1) not in explored:
                        frontier.append(SearchNode(
                            neighbor, parent=node,
                            path_cost=node.path_cost + weight, depth=node.depth + 1
                        ))

        return RouteResult("DLS", [], 0.0, 0, expanded_count)

    # =========================================================================
    # Algorithm 6: Iterative Deepening Search (IDS)
    # =========================================================================

    def ids_search(self, start: str, goal: str, max_depth: int = 8) -> RouteResult:
        """Repeatedly calls DLS with incrementing depth limits."""
        total_expanded = 0
        for depth_limit in range(max_depth + 1):
            res = self.dls_search(start, goal, limit=depth_limit)
            total_expanded += res.nodes_expanded
            if res.path:
                return RouteResult("IDS", res.path, res.total_cost, res.steps, total_expanded)

        return RouteResult("IDS", [], 0.0, 0, total_expanded)

    # =========================================================================
    # Algorithm 7: Greedy Best-First Search
    # =========================================================================

    def greedy_best_first(self, start: str, goal: str) -> RouteResult:
        """Evaluates nodes solely by heuristic distance to goal h(n)."""
        counter = 0
        h_init = self.graph.euclidean_heuristic(start, goal)
        frontier: List[Tuple[float, int, SearchNode]] = []
        heapq.heappush(frontier, (h_init, counter, SearchNode(start, heuristic_cost=h_init)))
        explored: Set[str] = set()
        expanded_count = 0

        while frontier:
            _, _, node = heapq.heappop(frontier)
            if node.state in explored:
                continue
            explored.add(node.state)
            expanded_count += 1

            if node.state == goal:
                path = node.reconstruct_path()
                cost = self._calculate_path_cost(path)
                return RouteResult("Greedy", path, cost, len(path) - 1, expanded_count)

            for neighbor, weight in self.graph.get_neighbors(node.state, weighted=True):
                if neighbor not in explored:
                    counter += 1
                    h_val = self.graph.euclidean_heuristic(neighbor, goal)
                    child = SearchNode(neighbor, parent=node, path_cost=node.path_cost + weight, heuristic_cost=h_val)
                    heapq.heappush(frontier, (h_val, counter, child))

        return RouteResult("Greedy", [], 0.0, 0, expanded_count)

    # =========================================================================
    # Algorithm 8: Recursive Best-First Search (RBFS)
    # =========================================================================

    def rbfs_search(self, start: str, goal: str) -> RouteResult:
        """Memory-bounded heuristic search simulating best-first in linear space."""
        h_val = self.graph.euclidean_heuristic(start, goal)
        root = SearchNode(start, path_cost=0.0, heuristic_cost=h_val)
        expanded = [0]

        def _rbfs(node: SearchNode, f_limit: float) -> Tuple[Optional[SearchNode], float]:
            expanded[0] += 1
            if node.state == goal:
                return node, node.total_cost

            successors: List[SearchNode] = []
            for neighbor, weight in self.graph.get_neighbors(node.state, weighted=True):
                # Avoid immediate cycle to parent
                if node.parent and neighbor == node.parent.state:
                    continue
                g = node.path_cost + weight
                h = self.graph.euclidean_heuristic(neighbor, goal)
                child = SearchNode(neighbor, parent=node, path_cost=g, heuristic_cost=h)
                child.total_cost = max(child.total_cost, node.total_cost)
                successors.append(child)

            if not successors:
                return None, float("inf")

            while True:
                successors.sort(key=lambda s: s.total_cost)
                best = successors[0]
                if best.total_cost > f_limit:
                    return None, best.total_cost

                alternative = successors[1].total_cost if len(successors) > 1 else float("inf")
                result, best.total_cost = _rbfs(best, min(f_limit, alternative))
                if result is not None:
                    return result, best.total_cost

        goal_node, _ = _rbfs(root, float("inf"))
        if goal_node:
            path = goal_node.reconstruct_path()
            return RouteResult("RBFS", path, goal_node.path_cost, len(path) - 1, expanded[0])
        return RouteResult("RBFS", [], 0.0, 0, expanded[0])

    # =========================================================================
    # Algorithm 9: Bidirectional BFS
    # =========================================================================

    def bidirectional_bfs(self, start: str, goal: str) -> RouteResult:
        """Searches simultaneously forward from start and backward from goal."""
        if start == goal:
            return RouteResult("Bi-BFS", [start], 0.0, 0, 1)

        forward_q = deque([SearchNode(start)])
        backward_q = deque([SearchNode(goal)])

        forward_visited: Dict[str, SearchNode] = {start: forward_q[0]}
        backward_visited: Dict[str, SearchNode] = {goal: backward_q[0]}
        expanded_count = 0

        intersection: Optional[str] = None

        while forward_q and backward_q:
            # Expand forward step
            curr_f = forward_q.popleft()
            expanded_count += 1
            for neighbor, weight in self.graph.get_neighbors(curr_f.state, weighted=True):
                if neighbor not in forward_visited:
                    child_f = SearchNode(neighbor, parent=curr_f, path_cost=curr_f.path_cost + weight)
                    forward_visited[neighbor] = child_f
                    forward_q.append(child_f)
                    if neighbor in backward_visited:
                        intersection = neighbor
                        break
            if intersection:
                break

            # Expand backward step
            curr_b = backward_q.popleft()
            expanded_count += 1
            for neighbor, weight in self.graph.get_neighbors(curr_b.state, weighted=True):
                if neighbor not in backward_visited:
                    child_b = SearchNode(neighbor, parent=curr_b, path_cost=curr_b.path_cost + weight)
                    backward_visited[neighbor] = child_b
                    backward_q.append(child_b)
                    if neighbor in forward_visited:
                        intersection = neighbor
                        break
            if intersection:
                break

        if not intersection:
            return RouteResult("Bi-BFS", [], 0.0, 0, expanded_count)

        # Merge forward path from start to intersection, and backward path from intersection to goal
        path_f = forward_visited[intersection].reconstruct_path()
        path_b = backward_visited[intersection].reconstruct_path()
        # path_b starts at goal and ends at intersection, reverse it from intersection to goal
        merged_path = path_f[:-1] + list(reversed(path_b))
        cost = self._calculate_path_cost(merged_path)

        return RouteResult("Bi-BFS", merged_path, cost, len(merged_path) - 1, expanded_count)

    # =========================================================================
    # Path Cost Helper
    # =========================================================================

    def _calculate_path_cost(self, path: List[str]) -> float:
        """Sums actual edge weights along a landmark sequence."""
        if not path or len(path) < 2:
            return 0.0
        total = 0.0
        for i in range(len(path) - 1):
            w = self.graph.get_edge_weight(path[i], path[i + 1])
            if w is not None:
                total += w
        return round(total, 3)
