"""
Campus Navigation Graph Module
Defines landmark coordinates, walkable edges, and spatial heuristics.
"""

import math
from typing import Dict, List, Tuple, Optional


class CampusGraph:
    """
    Graph representation of the campus layout with 13 landmarks and 19 edges.
    Supports both weighted (physical distance in km) and unweighted lookups.
    """

    # 2D Cartesian coordinates (x, y) for campus landmarks
    COORDINATES: Dict[str, Tuple[float, float]] = {
        "Main_Gate": (0.0, 4.0),
        "Bus_Stop": (0.0, 1.0),
        "Medical_Center": (1.0, 1.0),
        "Hostel": (2.0, 0.0),
        "Parking": (2.0, 4.0),
        "Admin_Block": (3.0, 5.0),
        "Cafeteria": (4.0, 1.0),
        "Student_Services": (6.0, 5.0),
        "Library": (6.0, 2.0),
        "Science_Block": (7.0, 1.0),
        "Exam_Hall": (8.0, 5.0),
        "AI_Lab": (9.0, 2.0),
        "Seminar_Room": (10.0, 4.0)
    }

    # Bidirectional campus pathways: (node_a, node_b, distance_km)
    RAW_EDGES: List[Tuple[str, str, float]] = [
        ("Main_Gate", "Bus_Stop", 1.0),
        ("Main_Gate", "Parking", 2.0),
        ("Main_Gate", "Admin_Block", 4.0),
        ("Main_Gate", "Hostel", 5.0),
        ("Bus_Stop", "Parking", 2.0),
        ("Bus_Stop", "Medical_Center", 2.0),
        ("Medical_Center", "Hostel", 3.0),
        ("Parking", "Science_Block", 3.0),
        ("Admin_Block", "Student_Services", 1.0),
        ("Admin_Block", "Exam_Hall", 2.0),
        ("Hostel", "Cafeteria", 2.0),
        ("Cafeteria", "Library", 2.0),
        ("Cafeteria", "Science_Block", 3.0),
        ("Student_Services", "Library", 2.0),
        ("Library", "AI_Lab", 3.0),
        ("Science_Block", "Exam_Hall", 3.0),
        ("Science_Block", "AI_Lab", 1.0),
        ("Science_Block", "Seminar_Room", 2.0),
        ("Exam_Hall", "Seminar_Room", 1.0),
    ]

    def __init__(self) -> None:
        # Adjacency list: node -> list of (neighbor, weight)
        self.adj_list: Dict[str, List[Tuple[str, float]]] = {
            node: [] for node in self.COORDINATES
        }
        self._build_graph()

    def _build_graph(self) -> None:
        """Populates bidirectional edges into the adjacency list."""
        for u, v, weight in self.RAW_EDGES:
            self.adj_list[u].append((v, weight))
            self.adj_list[v].append((u, weight))

    def is_valid_node(self, node: str) -> bool:
        """Returns True if the landmark exists in the graph."""
        return node in self.COORDINATES

    def get_coordinates(self, node: str) -> Tuple[float, float]:
        """Returns (x, y) coordinates for a given landmark."""
        if node not in self.COORDINATES:
            raise KeyError(f"Landmark '{node}' not found in campus graph.")
        return self.COORDINATES[node]

    def get_neighbors(self, node: str, weighted: bool = True) -> List[Tuple[str, float]]:
        """
        Returns adjacent nodes. If weighted=False, returns step cost of 1.0.
        """
        if node not in self.adj_list:
            raise KeyError(f"Landmark '{node}' not found in campus graph.")

        if weighted:
            return list(self.adj_list[node])
        return [(neighbor, 1.0) for neighbor, _ in self.adj_list[node]]

    def get_edge_weight(self, u: str, v: str) -> Optional[float]:
        """Returns distance between u and v if direct edge exists, else None."""
        if u not in self.adj_list:
            return None
        for neighbor, weight in self.adj_list[u]:
            if neighbor == v:
                return weight
        return None

    def euclidean_heuristic(self, current: str, goal: str, scale: float = 3.0) -> float:
        """
        Straight-line Euclidean distance between two landmarks.
        Scaled by the grid-to-pathway ratio (3.0) to strictly guarantee
        mathematical admissibility (h(n) <= h*(n)) for A* optimal pathfinding.
        """
        x1, y1 = self.get_coordinates(current)
        x2, y2 = self.get_coordinates(goal)
        raw_dist = math.hypot(x2 - x1, y2 - y1)
        return raw_dist / scale if scale > 0 else raw_dist

    def raw_euclidean_distance(self, current: str, goal: str) -> float:
        """Calculates unscaled straight-line Euclidean distance."""
        return self.euclidean_heuristic(current, goal, scale=1.0)

    def get_all_nodes(self) -> List[str]:
        """Returns sorted list of all landmark names."""
        return sorted(self.COORDINATES.keys())
