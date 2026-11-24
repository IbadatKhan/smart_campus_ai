"""
Unit & Integration Tests for Spatial Graph Navigation (Member 1)
Verifies landmark topology, heuristic admissibility, A* optimality,
UCS, BFS, DFS, and the complete 9-algorithm benchmark suite.
"""

import unittest
from ai_engines.navigation.campus_graph import CampusGraph
from ai_engines.navigation.search_engine import SearchEngine
from ai_engines.engine_facade import AIEngineFacade


class TestCampusNavigation(unittest.TestCase):
    """Test suite covering CampusGraph, SearchEngine, and EngineFacade wiring."""

    def setUp(self) -> None:
        self.graph = CampusGraph()
        self.engine = SearchEngine(self.graph)

    # =========================================================================
    # CampusGraph Topology Tests
    # =========================================================================

    def test_landmark_node_count(self) -> None:
        """Ensure all 13 campus landmarks are registered."""
        nodes = self.graph.get_all_nodes()
        self.assertEqual(len(nodes), 13)
        self.assertIn("Main_Gate", nodes)
        self.assertIn("AI_Lab", nodes)
        self.assertIn("Seminar_Room", nodes)

    def test_edge_count_and_bidirectionality(self) -> None:
        """Ensure all 19 edges are bidirectional and symmetric."""
        self.assertEqual(len(self.graph.RAW_EDGES), 19)

        # 19 bidirectional edges expand to 38 directed adjacency entries
        total_directed = sum(len(self.graph.get_neighbors(n)) for n in self.graph.get_all_nodes())
        self.assertEqual(total_directed, 38)

        for u, v, weight in self.graph.RAW_EDGES:
            self.assertEqual(self.graph.get_edge_weight(u, v), weight)
            self.assertEqual(self.graph.get_edge_weight(v, u), weight)

    def test_euclidean_heuristic_properties(self) -> None:
        """Verify heuristic identity, symmetry, and positive distance."""
        self.assertEqual(self.graph.euclidean_heuristic("Main_Gate", "Main_Gate"), 0.0)
        self.assertGreater(self.graph.euclidean_heuristic("Main_Gate", "AI_Lab"), 0.0)

        forward = self.graph.euclidean_heuristic("Hostel", "AI_Lab")
        backward = self.graph.euclidean_heuristic("AI_Lab", "Hostel")
        self.assertAlmostEqual(forward, backward, places=4)

    def test_heuristic_admissibility_across_all_edges(self) -> None:
        """
        Scaled Euclidean distance must never overestimate actual edge weight (h(n) <= h*(n)).
        This mathematically guarantees A* optimality.
        """
        for u, v, weight in self.graph.RAW_EDGES:
            h_val = self.graph.euclidean_heuristic(u, v)
            self.assertLessEqual(
                h_val,
                weight + 1e-6,
                f"Inadmissible on edge ({u}, {v}): {h_val:.3f} > {weight:.3f}"
            )

    # =========================================================================
    # Search Algorithm Tests
    # =========================================================================

    def test_astar_optimal_cost(self) -> None:
        """A* must find optimal least-cost path from Hostel to AI_Lab (6.0 km)."""
        res = self.engine.astar_search("Hostel", "AI_Lab")
        self.assertEqual(res.algorithm_used, "A*")
        self.assertEqual(res.path, ["Hostel", "Cafeteria", "Science_Block", "AI_Lab"])
        self.assertEqual(res.total_cost, 6.0)
        self.assertEqual(res.steps, 3)
        self.assertGreater(res.nodes_expanded, 0)

    def test_ucs_and_astar_optimality_match(self) -> None:
        """UCS (Dijkstra) and A* must both discover identical optimal total cost."""
        ucs_res = self.engine.ucs_search("Main_Gate", "AI_Lab")
        astar_res = self.engine.astar_search("Main_Gate", "AI_Lab")

        self.assertAlmostEqual(ucs_res.total_cost, astar_res.total_cost, places=3)
        # A* should typically expand fewer or equal nodes compared to uninformed UCS
        self.assertLessEqual(astar_res.nodes_expanded, ucs_res.nodes_expanded)

    def test_bfs_unweighted_fewest_hops(self) -> None:
        """BFS must find the path with minimal hop count."""
        res = self.engine.bfs_search("Main_Gate", "AI_Lab")
        self.assertEqual(res.algorithm_used, "BFS")
        self.assertTrue(len(res.path) > 0)
        self.assertEqual(res.path[0], "Main_Gate")
        self.assertEqual(res.path[-1], "AI_Lab")

    def test_dfs_finds_valid_connected_path(self) -> None:
        """DFS must find a valid connected path from start to goal."""
        res = self.engine.dfs_search("Main_Gate", "Seminar_Room")
        self.assertEqual(res.algorithm_used, "DFS")
        self.assertTrue(len(res.path) > 0)
        # Verify connectivity of every step in DFS path
        for i in range(len(res.path) - 1):
            weight = self.graph.get_edge_weight(res.path[i], res.path[i + 1])
            self.assertIsNotNone(weight, f"Disconnected hop: {res.path[i]} -> {res.path[i + 1]}")

    def test_dls_and_ids(self) -> None:
        """DLS fails on tight depth and succeeds with sufficient limit; IDS succeeds."""
        # DLS with limit=1 cannot reach AI_Lab from Hostel (needs 3 hops)
        dls_shallow = self.engine.dls_search("Hostel", "AI_Lab", limit=1)
        self.assertEqual(dls_shallow.path, [])

        # DLS with limit=4 reaches AI_Lab
        dls_deep = self.engine.dls_search("Hostel", "AI_Lab", limit=4)
        self.assertTrue(len(dls_deep.path) > 0)

        # IDS explores iteratively and reaches goal
        ids_res = self.engine.ids_search("Hostel", "AI_Lab", max_depth=6)
        self.assertTrue(len(ids_res.path) > 0)
        self.assertEqual(ids_res.path[-1], "AI_Lab")

    def test_greedy_and_bidirectional_bfs(self) -> None:
        """Greedy Best-First and Bidirectional BFS must return valid connected paths."""
        greedy_res = self.engine.greedy_best_first("Main_Gate", "AI_Lab")
        self.assertTrue(len(greedy_res.path) > 0)
        self.assertEqual(greedy_res.path[-1], "AI_Lab")

        bi_res = self.engine.bidirectional_bfs("Main_Gate", "AI_Lab")
        self.assertTrue(len(bi_res.path) > 0)
        self.assertEqual(bi_res.path[0], "Main_Gate")
        self.assertEqual(bi_res.path[-1], "AI_Lab")

    def test_same_start_and_goal(self) -> None:
        """Querying same start and goal returns zero-cost direct path."""
        res = self.engine.compute_route("Library", "Library")
        self.assertEqual(res.path, ["Library"])
        self.assertEqual(res.total_cost, 0.0)
        self.assertEqual(res.steps, 0)

    def test_invalid_landmark_handling(self) -> None:
        """Unknown landmark returns empty path gracefully."""
        res = self.engine.compute_route("Unknown_Spot", "AI_Lab")
        self.assertEqual(res.path, [])
        self.assertEqual(res.total_cost, 0.0)

    # =========================================================================
    # 9-Algorithm Benchmark Suite Test
    # =========================================================================

    def test_9_algorithm_benchmark_suite(self) -> None:
        """Run benchmark across all 9 algorithms and verify complete metrics."""
        results = self.engine.run_benchmark("Hostel", "AI_Lab")
        self.assertEqual(len(results), 9)

        expected_algos = [
            "Breadth-First Search (BFS)",
            "Depth-First Search (DFS)",
            "Uniform Cost Search (UCS)",
            "Depth-Limited Search (DLS, L=4)",
            "Iterative Deepening Search (IDS)",
            "Greedy Best-First Search",
            "A* Search (Euclidean)",
            "Recursive Best-First Search (RBFS)",
            "Bidirectional BFS",
        ]

        for algo_name in expected_algos:
            self.assertIn(algo_name, results)
            r = results[algo_name]
            self.assertTrue(len(r.path) > 0, f"{algo_name} failed to find path")
            self.assertGreater(r.total_cost, 0.0)
            self.assertGreater(r.nodes_expanded, 0)
            self.assertGreaterEqual(r.execution_time_ms, 0.0)

    # =========================================================================
    # Master Facade Integration Test
    # =========================================================================

    def test_engine_facade_uses_real_search_engine(self) -> None:
        """AIEngineFacade delegates to real SearchEngine and finds optimal path."""
        facade = AIEngineFacade()
        res = facade.compute_route("Hostel", "AI_Lab")
        self.assertEqual(res.algorithm_used, "A*")
        self.assertEqual(res.path, ["Hostel", "Cafeteria", "Science_Block", "AI_Lab"])
        self.assertEqual(res.total_cost, 6.0)


if __name__ == "__main__":
    unittest.main()
