"""
Module: presentation.cli_view
Description: Presentation Layer (CLI Form & Interactive Terminal UI).
Provides clean prompts, formatted ASCII tables, and pre-set test scenarios.
Contains ZERO mathematical algorithms or graph representations.
"""

from typing import Optional
from core.core_facade import CoreFacade
from core.models import UniversalRequest, FinalResponse


class InteractiveCampusCLI:
    """
    Presentation Layer Controller:
    Communicates ONLY with CoreFacade (Master Facade 1).
    Collects user inputs into UniversalRequest DTOs and renders FinalResponse.
    """

    def __init__(self, core_facade: CoreFacade) -> None:
        """
        Initializes the CLI controller with the core system facade.
        """
        self.facade = core_facade

    def start(self) -> None:
        """
        Main interactive loop for the campus command-line interface.
        Displays menus, accepts user inputs, and delegates actions.
        """
        while True:
            self._print_header()
            print("  1. Submit Custom Campus Request")
            print("  2. Run Pre-Set Test Scenarios (Canonical SRS Test Suite)")
            print("  3. Run 9-Algorithm Pathfinding Benchmark Suite")
            print("  4. Launch Graphical Campus Map Window (Tkinter GUI)")
            print("  5. Exit")
            print("=" * 65)

            choice = input("\nSelect an option [1-5]: ").strip()
            if choice == "1":
                self._handle_custom_request()
            elif choice == "2":
                self._handle_preset_scenarios()
            elif choice == "3":
                self._handle_benchmark()
            elif choice == "4":
                self._handle_gui_launch()
            elif choice == "5":
                print("\nExiting Smart Campus AI System. Goodbye!")
                break
            else:
                print("\n[!] Invalid choice. Please select an option between 1 and 5.")
            input("\nPress Enter to return to main menu...")

    def _print_header(self) -> None:
        """
        Prints the ASCII header banner for the Smart Campus AI application.
        """
        print("\n" + "=" * 65)
        print("     SMART CAMPUS AI DECISION SUPPORT & AUTOMATION SYSTEM")
        print("          FAST-NUCES Fall 2026 - AI Lab Capstone")
        print("=" * 65)

    def _handle_custom_request(self) -> None:
        """
        Collects structured form input fields tailored to the chosen request type.
        Builds a UniversalRequest DTO and dispatches it through CoreFacade.
        """
        print("\n--- Submit Custom Campus Request ---")
        name = input("Enter Name [default: Ali]: ").strip() or "Ali"

        print("Roles: [1] student  [2] instructor  [3] staff")
        r_choice = input("Select Role [1-3, default 1]: ").strip()
        role = {"1": "student", "2": "instructor", "3": "staff"}.get(r_choice, "student")

        print("\nRequest Types:")
        print("  [1] Navigation_Only")
        print("  [2] Eligibility_Check")
        print("  [3] Booking_or_Scheduling")
        print("  [4] Urgent_Service_Request")
        print("  [5] Full_Service_Request")
        t_choice = input("Select Request Type [1-5, default 5]: ").strip()
        req_types = {
            "1": "Navigation_Only",
            "2": "Eligibility_Check",
            "3": "Booking_or_Scheduling",
            "4": "Urgent_Service_Request",
            "5": "Full_Service_Request"
        }
        req_type = req_types.get(t_choice, "Full_Service_Request")

        curr_loc = "Hostel"
        dest = "AI_Lab"
        category = "AI_Lab_Support"
        query_str = ""
        preferred_slot = 2
        sev = 5
        time_sens = 5
        crowd = 5
        desc = ""

        if req_type == "Navigation_Only":
            curr_loc = input("Current Location [default: Hostel]: ").strip() or "Hostel"
            dest = input("Destination Landmark [default: AI_Lab]: ").strip() or "AI_Lab"

        elif req_type == "Eligibility_Check":
            print("\nEnter FOL query predicate:")
            print("Examples: UsesLab(DrKhan, Lab1), Eligible(Ali, AI), UsesLab(Ali, Lab1)")
            query_str = input("Query [default: UsesLab(DrKhan, Lab1)]: ").strip() or "UsesLab(DrKhan, Lab1)"

        elif req_type == "Booking_or_Scheduling":
            category = input("Category (AI_Lab_Support / Viva_Scheduling) [default: AI_Lab_Support]: ").strip() or "AI_Lab_Support"
            curr_loc = input("Current Location [default: Hostel]: ").strip() or "Hostel"
            slot_str = input("Preferred Slot (1-4) [default 2]: ").strip() or "2"
            preferred_slot = int(slot_str) if slot_str.isdigit() else 2

        elif req_type in ["Urgent_Service_Request", "Full_Service_Request"]:
            category = input("Category [default: AI_Lab_Support]: ").strip() or "AI_Lab_Support"
            curr_loc = input("Current Location [default: Hostel]: ").strip() or "Hostel"
            dest = input("Destination [default: AI_Lab]: ").strip() or "AI_Lab"
            slot_str = input("Preferred Slot (1-4) [default 2]: ").strip() or "2"
            preferred_slot = int(slot_str) if slot_str.isdigit() else 2

            sev_str = input("Severity (1-10) [default 8]: ").strip() or "8"
            sev = int(sev_str) if sev_str.isdigit() else 8

            time_str = input("Time Sensitivity (1-10) [default 9]: ").strip() or "9"
            time_sens = int(time_str) if time_str.isdigit() else 9

            crowd_str = input("Crowd Level (1-10) [default 5]: ").strip() or "5"
            crowd = int(crowd_str) if crowd_str.isdigit() else 5

            desc = input("Description Note (optional): ").strip()

        req = UniversalRequest(
            request_id="REQ-USER-001",
            name=name,
            role=role,
            request_type=req_type,
            category=category,
            current_location=curr_loc,
            destination=dest,
            preferred_slot=preferred_slot,
            severity=sev,
            time_sensitivity=time_sens,
            crowd_level=crowd,
            query=query_str,
            description_note=desc
        )

        print("\n[+] Dispatching request through CoreFacade...")
        response = self.facade.execute(req)
        self.render_response(response)

    def _handle_preset_scenarios(self) -> None:
        """
        Executes pre-configured canonical test scenarios demonstrating each pipeline.
        """
        print("\n--- Canonical Pre-Set Test Scenarios (from SRS) ---")
        print("  [1] Ali: Full Service Request for AI Lab Support")
        print("  [2] Dr. Khan: Instructor Lab Access Verification (FOL Query)")
        print("  [3] Sara: Presentation Slot Scheduling (CSP)")
        print("  [4] Usman: Urgent Equipment Maintenance (High ANN Severity)")
        print("  [5] Guest: Navigation Only (Main Gate to Cafeteria)")
        print("  [6] Unregistered User: Security Gatekeeper Rejection Test")

        s_choice = input("\nSelect scenario [1-6]: ").strip()
        scenarios = {
            "1": UniversalRequest("REQ-101", "Ali", "student", "Full_Service_Request", "AI_Lab_Support", "Hostel", "AI_Lab", 2, 8, 9, 5),
            "2": UniversalRequest("REQ-102", "DrKhan", "instructor", "Eligibility_Check", "Access_Request", "Admin_Block", "AI_Lab", 1, 3, 2, 2, query="UsesLab(DrKhan, Lab1)"),
            "3": UniversalRequest("REQ-103", "Sara", "student", "Booking_or_Scheduling", "Viva_Scheduling", "Library", "Seminar_Room", 2, 4, 4, 3),
            "4": UniversalRequest("REQ-104", "Usman", "staff", "Urgent_Service_Request", "Maintenance", "Science_Block", "Exam_Hall", 3, 9, 10, 6),
            "5": UniversalRequest("REQ-105", "Guest", "student", "Navigation_Only", "Access_Request", "Main_Gate", "Cafeteria", 1, 1, 1, 2),
            "6": UniversalRequest("REQ-106", "Intruder", "unregistered", "Full_Service_Request", "Access_Request", "Hostel", "Admin_Block", 1, 5, 5, 5)
        }

        req = scenarios.get(s_choice)
        if not req:
            print("[!] Invalid scenario choice.")
            return

        print(f"\n[+] Executing Scenario '{req.request_id}' ({req.request_type})...")
        response = self.facade.execute(req)
        self.render_response(response)

    def _handle_benchmark(self) -> None:
        """
        Runs the 9-algorithm pathfinding benchmark between two landmarks.
        Displays comparative cost, step count, expanded nodes, and runtime in ms.
        """
        print("\n--- 9-Algorithm Pathfinding Benchmark Suite ---")
        start = input("Start Landmark [default: Main_Gate]: ").strip() or "Main_Gate"
        goal = input("Goal Landmark [default: AI_Lab]: ").strip() or "AI_Lab"

        print(f"\n[+] Running benchmark comparison from '{start}' to '{goal}'...")
        results = self.facade.run_navigation_benchmark(start, goal)

        print("\n" + "-" * 75)
        print(f"{'Algorithm':<22} | {'Cost':<8} | {'Hops':<6} | {'Expanded':<10} | {'Time (ms)':<10}")
        print("-" * 75)
        for algo, res in results.items():
            print(f"{algo:<22} | {res.total_cost:<8.1f} | {len(res.path):<6} | {res.nodes_expanded:<10} | {res.execution_time_ms:<10.3f}")
        print("-" * 75)

    def _handle_gui_launch(self) -> None:
        """
        Launches the advanced Tkinter graphical canvas window for visual navigation.
        """
        try:
            from presentation.gui_advanced import launch_gui
            print("\n[+] Opening Graphical Campus Map Window...")
            launch_gui(self.facade)
        except Exception as e:
            print(f"\n[!] Error launching GUI: {str(e)}")

    def render_response(self, response: FinalResponse) -> None:
        """
        Renders a standardized ASCII Decision Card summarizing the multi-module output.
        """
        status_banner = " [ACCEPTED] " if response.decision == "accepted" else " [REJECTED] "
        print("\n" + "=" * 65)
        print(f" DECISION RESULT: {status_banner}")
        print(f" Request ID: {response.request_id}")
        print("=" * 65)

        if response.priority:
            p = response.priority
            print(f" • Urgency (Perceptron) : {p.binary_priority.upper()}")
            print(f" • Priority (MLP Model) : {p.final_priority.upper()} (Confidence: {p.confidence * 100:.1f}%)")

        if response.eligibility:
            e = response.eligibility
            status = "AUTHORIZED" if e.allowed else "ACCESS DENIED"
            print(f" • Gatekeeper Logic     : {status}")
            print(f"   Reason               : {e.explanation}")

        if response.assignment:
            a = response.assignment
            print(f" • CSP Room Allocated   : {a.assigned_room} (Slot {a.assigned_slot})")
            if a.notes:
                print(f"   Notes                : {a.notes}")

        if response.route and response.route.path:
            r = response.route
            print(f" • Navigation Engine    : {r.algorithm_used}")
            print(f"   Optimal Route        : {' -> '.join(r.path)}")
            print(f"   Walking Cost         : {r.total_cost:.1f} minutes ({len(r.path) - 1} hops)")

        print("-" * 65)
        print(f" Summary: {response.message}")
        print("=" * 65)
