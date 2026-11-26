"""
Module: presentation.gui_advanced
Description: Advanced Graphical Tkinter Window for visual campus navigation.
Renders 13 campus landmarks, 19 edges, real-time A* path highlighting,
and algorithm benchmark comparisons on a 2D graphical canvas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple, Optional
from core.core_facade import CoreFacade
from ai_engines.navigation.campus_graph import CampusGraph


class CampusVisualizerGUI:
    """
    Tkinter-based Visual Campus Map and Algorithm Demonstration Window.
    Provides interactive pathfinding visualization and benchmark execution.
    """

    def __init__(self, root: tk.Tk, facade: CoreFacade) -> None:
        """
        Initializes the campus map window with visual widgets and layout.
        """
        self.root = root
        self.facade = facade
        self.root.title("Smart Campus AI - Interactive Spatial Navigator")
        self.root.geometry("980x680")
        self.root.minsize(900, 600)

        # Scale parameters for canvas rendering
        self.offset_x = 70
        self.offset_y = 380
        self.scale_x = 80
        self.scale_y = 65

        # Path highlighting storage
        self.highlighted_edges: List[int] = []
        self.highlighted_nodes: List[int] = []

        self._build_ui()
        self._draw_base_graph()

    def _coord_to_canvas(self, x: float, y: float) -> Tuple[float, float]:
        """
        Converts campus Cartesian coordinates (x, y) to canvas pixel coordinates.
        Inverts Y axis so (0, 0) is at the bottom-left of the campus map.
        """
        cx = self.offset_x + x * self.scale_x
        cy = self.offset_y - y * self.scale_y
        return cx, cy

    def _build_ui(self) -> None:
        """
        Constructs the top toolbar, canvas area, and bottom metric panels.
        """
        # Top control frame
        ctrl_frame = ttk.LabelFrame(self.root, text=" Navigation Controls ", padding=10)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=12, pady=8)

        landmarks = list(CampusGraph.COORDINATES.keys())

        # Start landmark selection
        ttk.Label(ctrl_frame, text="Start:").grid(row=0, column=0, padx=4, sticky=tk.W)
        self.start_var = tk.StringVar(value="Hostel")
        self.start_combo = ttk.Combobox(ctrl_frame, textvariable=self.start_var, values=landmarks, width=15, state="readonly")
        self.start_combo.grid(row=0, column=1, padx=4)

        # Destination landmark selection
        ttk.Label(ctrl_frame, text="Destination:").grid(row=0, column=2, padx=4, sticky=tk.W)
        self.goal_var = tk.StringVar(value="AI_Lab")
        self.goal_combo = ttk.Combobox(ctrl_frame, textvariable=self.goal_var, values=landmarks, width=15, state="readonly")
        self.goal_combo.grid(row=0, column=3, padx=4)

        # Action buttons
        btn_find = ttk.Button(ctrl_frame, text="Find Shortest Path (A*)", command=self._on_find_path)
        btn_find.grid(row=0, column=4, padx=8)

        btn_bench = ttk.Button(ctrl_frame, text="Run 9-Algorithm Benchmark", command=self._on_run_benchmark)
        btn_bench.grid(row=0, column=5, padx=4)

        btn_reset = ttk.Button(ctrl_frame, text="Reset Map", command=self._on_reset)
        btn_reset.grid(row=0, column=6, padx=4)

        # Canvas frame
        map_frame = ttk.LabelFrame(self.root, text=" Campus Topological Map (13 Landmarks & 19 Pathways) ", padding=5)
        map_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.canvas = tk.Canvas(map_frame, bg="#fcfcfc", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bottom output frame
        out_frame = ttk.LabelFrame(self.root, text=" Output Metrics & Route Details ", padding=8)
        out_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=8)

        self.status_var = tk.StringVar(value="Select start and destination landmarks, then click 'Find Shortest Path'.")
        status_lbl = ttk.Label(out_frame, textvariable=self.status_var, font=("Segoe UI", 10, "bold"), foreground="#1a365d")
        status_lbl.pack(side=tk.TOP, anchor=tk.W, pady=2)

        self.output_text = tk.Text(out_frame, height=4, wrap=tk.WORD, font=("Consolas", 9), bg="#f8fafc", relief=tk.SOLID, borderwidth=1)
        self.output_text.pack(fill=tk.X, pady=4)

    def _draw_base_graph(self) -> None:
        """
        Draws the static campus pathways and landmark circles onto the canvas.
        """
        self.canvas.delete("all")
        self.highlighted_edges.clear()
        self.highlighted_nodes.clear()

        # 1. Draw 19 raw edges with weights
        for u, v, weight in CampusGraph.RAW_EDGES:
            ux, uy = self._coord_to_canvas(*CampusGraph.COORDINATES[u])
            vx, vy = self._coord_to_canvas(*CampusGraph.COORDINATES[v])

            # Draw edge line
            self.canvas.create_line(ux, uy, vx, vy, fill="#94a3b8", width=2, tags="edge")

            # Draw weight label at midpoint
            mx, my = (ux + vx) / 2.0, (uy + vy) / 2.0
            self.canvas.create_text(mx, my - 6, text=f"{weight:.0f}", fill="#64748b", font=("Segoe UI", 8, "bold"))

        # 2. Draw 13 landmark nodes
        radius = 18
        for name, (x, y) in CampusGraph.COORDINATES.items():
            cx, cy = self._coord_to_canvas(x, y)
            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill="#e0f2fe", outline="#0284c7", width=2, tags=f"node_{name}"
            )
            self.canvas.create_text(
                cx, cy + radius + 10,
                text=name, fill="#0f172a", font=("Segoe UI", 9, "bold")
            )

    def _on_find_path(self) -> None:
        """
        Computes the optimal route via CoreFacade and highlights the path on the canvas.
        """
        start = self.start_var.get()
        goal = self.goal_var.get()

        if start == goal:
            messagebox.showinfo("Navigation", f"Start and Destination are both '{start}'. Distance is 0 km.")
            return

        # Clear previous highlights
        self._clear_highlights()

        # Direct optimal path computation via CoreFacade
        astar_res = self.facade.compute_route(start, goal)

        if not astar_res or not astar_res.path:
            self.status_var.set(f"[!] No viable route found between '{start}' and '{goal}'.")
            return

        path = astar_res.path
        cost = astar_res.total_cost

        # Highlight path edges
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            ux, uy = self._coord_to_canvas(*CampusGraph.COORDINATES[u])
            vx, vy = self._coord_to_canvas(*CampusGraph.COORDINATES[v])
            line_id = self.canvas.create_line(ux, uy, vx, vy, fill="#ea580c", width=5)
            self.highlighted_edges.append(line_id)

        # Highlight path nodes
        radius = 20
        for node in path:
            cx, cy = self._coord_to_canvas(*CampusGraph.COORDINATES[node])
            fill_color = "#22c55e" if node == path[0] else ("#ef4444" if node == path[-1] else "#fbbf24")
            node_id = self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=fill_color, outline="#78350f", width=2
            )
            self.highlighted_nodes.append(node_id)
            # Re-draw text
            txt_id = self.canvas.create_text(cx, cy, text=node[:3], fill="#ffffff", font=("Segoe UI", 8, "bold"))
            self.highlighted_nodes.append(txt_id)

        self.status_var.set(f"Optimal Path Found (A*): {' -> '.join(path)}  |  Total Cost: {cost:.1f} km  |  Hops: {len(path)-1}")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(
            tk.END,
            f"Algorithm: A* (Admissible Euclidean Heuristic)\n"
            f"Path Sequence: {' -> '.join(path)}\n"
            f"Metrics: Cost = {cost:.1f} km | Hops = {len(path)-1} | Nodes Expanded = {astar_res.nodes_expanded} | Runtime = {astar_res.execution_time_ms:.3f} ms"
        )

    def _on_run_benchmark(self) -> None:
        """
        Executes the 9-algorithm benchmark suite and renders results in the output pane.
        """
        start = self.start_var.get()
        goal = self.goal_var.get()

        results = self.facade.run_navigation_benchmark(start, goal)
        self.output_text.delete("1.0", tk.END)
        header = f"{'Algorithm':<36} | {'Cost':<8} | {'Hops':<6} | {'Expanded':<10} | {'Time (ms)':<10}\n"
        div = "-" * 78 + "\n"
        self.output_text.insert(tk.END, f"Benchmark Comparison: {start} -> {goal}\n" + div + header + div)

        for algo, r in results.items():
            line = f"{algo:<36} | {r.total_cost:<8.1f} | {len(r.path):<6} | {r.nodes_expanded:<10} | {r.execution_time_ms:<10.3f}\n"
            self.output_text.insert(tk.END, line)

        self.status_var.set(f"Completed 9-algorithm benchmark between '{start}' and '{goal}'. See table below.")

    def _clear_highlights(self) -> None:
        """
        Removes all highlight overlays from the canvas.
        """
        for item in self.highlighted_edges:
            self.canvas.delete(item)
        for item in self.highlighted_nodes:
            self.canvas.delete(item)
        self.highlighted_edges.clear()
        self.highlighted_nodes.clear()

    def _on_reset(self) -> None:
        """
        Clears all highlights and resets output metrics to default state.
        """
        self._clear_highlights()
        self.status_var.set("Map reset. Select landmarks and click 'Find Shortest Path'.")
        self.output_text.delete("1.0", tk.END)


def launch_gui(facade: CoreFacade) -> None:
    """
    Launches the standalone Tkinter graphical campus navigation window.
    """
    root = tk.Tk()
    CampusVisualizerGUI(root, facade)
    root.mainloop()
