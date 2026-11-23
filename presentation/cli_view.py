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
        self.facade = core_facade

    def start(self) -> None:
        """Main loop for the interactive terminal application."""
        while True:
            self._print_header()
            print("  1. Submit Custom Campus Request")
            print("  2. Run Pre-Set Test Scenarios (Canonical SRS Test Suite)")
            print("  3. Run 9-Algorithm Pathfinding Benchmark Suite")
            print("  4. Exit")
            print("=" * 65)

            choice = input("\nSelect an option [1-4]: ").strip()
            if choice == "1":
                self._handle_custom_request()
            elif choice == "2":
                self._handle_preset_scenarios()
            elif choice == "3":
                self._handle_benchmark()
            elif choice == "4":
                print("\nExiting Smart Campus AI System. Goodbye!")
                break
            else:
                print("\n[!] Invalid choice. Please select 1, 2, 3, or 4.")
            input("\nPress Enter to return to main menu...")

    def _print_header(self) -> None:
        print("\n" + "=" * 65)
        print("     SMART CAMPUS AI DECISION SUPPORT & AUTOMATION SYSTEM")
        print("          FAST-NUCES Fall 2026 - AI Lab Capstone")
        print("=" * 65)

    def _handle_custom_request(self) -> None:
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

        curr_loc = input("Current Location [default: Hostel]: ").strip() or "Hostel"
        dest = input("Destination [default: AI_Lab]: ").strip() or "AI_Lab"

        sev_str = input("Severity (1-10) [default 7]: ").strip() or "7"
        sev = int(sev_str) if sev_str.isdigit() else 7

        time_str = input("Time Sensitivity (1-10) [default 8]: ").strip() or "8"
        time_sens = int(time_str) if time_str.isdigit() else 8

        crowd_str = input("Crowd Level (1-10) [default 5]: ").strip() or "5"
        crowd = int(crowd_str) if crowd_str.isdigit() else 5

        req = UniversalRequest(
            request_id="REQ-USER-001",
            name=name,
            role=role,
            request_type=req_type,
            category="AI_Lab_Support",
            current_location=curr_loc,
            destination=dest,
            severity=sev,
            time_sensitivity=time_sens,
            crowd_level=crowd,
            preferred_slot=2
        )

        print("\n[+] Dispatching request through CoreFacade...")
        response = self.facade.execute(req)
        self.render_response(response)

    def _handle_preset_scenarios(self) -> None:
        print("\n--- Canonical Pre-Set Test Scenarios (from SRS) ---")
        print("  [1] Ali: Full Service Request for AI Lab Support")
        print("  [2] Dr. Khan: Instructor Lab Access Verification")
        print("  [3] Sara: Presentation Slot Scheduling (CSP)")
        print("  [4] Usman: Urgent Equipment Maintenance (High ANN Severity)")
        print("  [5] Guest: Navigation Only (Main Gate to Cafeteria)")
        print("  [6] Unregistered User: Security Gatekeeper Rejection Test")

        s_choice = input("\nSelect scenario [1-6]: ").strip()
        scenarios = {
            "1": UniversalRequest("REQ-101", "Ali", "student", "Full_Service_Request", "AI_Lab_Support", "Hostel", "AI_Lab", 2, 8, 9, 5),
            "2": UniversalRequest("REQ-102", "DrKhan", "instructor", "Eligibility_Check", "Access_Request", "Admin_Block", "AI_Lab", 1, 3, 2, 2),
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

    def render_response(self, response: FinalResponse) -> None:
        """Renders formatted ASCII response card."""
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
