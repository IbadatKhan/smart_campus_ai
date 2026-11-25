"""
Unit Tests for Symbolic Reasoning & Constraint Satisfaction (Member 2)
Verifies First-Order Logic forward chaining, security gatekeeper access/rejection,
and the 6-group viva CSP solver (MRV, Degree, LCV, Forward Checking).
"""

import unittest
from ai_engines.reasoning.logic_kb import FOLPredicate, FOLRule, FOLKnowledgeBase, LogicKBGatekeeper
from ai_engines.reasoning.csp_scheduler import TimetableCSPProblem, CSPScheduler


class TestSymbolicLogicKB(unittest.TestCase):
    """Test suite for First-Order Logic Knowledge Base and Gatekeeper."""

    def setUp(self) -> None:
        self.kb = FOLKnowledgeBase()
        self.gatekeeper = LogicKBGatekeeper(self.kb)

    def test_initial_facts_loaded(self) -> None:
        """Ensure default campus facts are registered in working memory."""
        self.assertIn(FOLPredicate("Student", "Ali"), self.kb.facts)
        self.assertIn(FOLPredicate("Student", "Sara"), self.kb.facts)
        self.assertIn(FOLPredicate("Completed", "Ali", "ProgrammingFundamentals"), self.kb.facts)
        self.assertIn(FOLPredicate("Teaches", "DrKhan", "AI"), self.kb.facts)

    def test_forward_chaining_rule_r1_ali_eligible(self) -> None:
        """
        Rule R1: Student(x) ^ Completed(x, ProgrammingFundamentals) => Eligible(x, AI)
        Ali satisfies both antecedents, so Eligible(Ali, AI) must be entailed.
        """
        query = FOLPredicate("Eligible", "Ali", "AI")
        entailed, trace = self.kb.forward_chain(query)
        self.assertTrue(entailed)
        self.assertTrue(len(trace) > 0)
        self.assertIn(query, self.kb.facts)

    def test_gatekeeper_rejection_for_sara(self) -> None:
        """
        Sara is a Student but has NOT completed ProgrammingFundamentals.
        The gatekeeper must reject Sara for AI_Lab_Support (circuit breaker).
        """
        res = self.gatekeeper.verify_request_eligibility(
            user_name="Sara",
            role="student",
            category="AI_Lab_Support"
        )
        self.assertFalse(res.allowed)
        self.assertIn("Access denied", res.explanation)
        self.assertIn("ProgrammingFundamentals", res.explanation)

    def test_gatekeeper_approval_for_ali(self) -> None:
        """Ali has completed prerequisites; gatekeeper must grant access."""
        res = self.gatekeeper.verify_request_eligibility(
            user_name="Ali",
            role="student",
            category="AI_Lab_Support"
        )
        self.assertTrue(res.allowed)
        self.assertIn("Access granted", res.explanation)

    def test_viva_scheduling_role_authorization(self) -> None:
        """Faculty and staff can schedule vivas; students are rejected."""
        instructor_res = self.gatekeeper.verify_request_eligibility(
            user_name="DrKhan",
            role="instructor",
            category="Viva_Scheduling"
        )
        self.assertTrue(instructor_res.allowed)

        student_res = self.gatekeeper.verify_request_eligibility(
            user_name="Ali",
            role="student",
            category="Viva_Scheduling"
        )
        self.assertFalse(student_res.allowed)


class TestCSPScheduler(unittest.TestCase):
    """Test suite for the 6-group examination timetable CSP solver."""

    def setUp(self) -> None:
        self.problem = TimetableCSPProblem()
        self.scheduler = CSPScheduler(self.problem)

    def test_6_group_timetable_solution_exists(self) -> None:
        """Backtracking solver must find a valid complete timetable for G1 to G6."""
        res = self.scheduler.solve_group_timetable()
        self.assertTrue(res.success)
        self.assertEqual(len(res.timetable), 6)

        timetable = res.timetable
        for var in ["G1", "G2", "G3", "G4", "G5", "G6"]:
            self.assertIn(var, timetable)
            self.assertIn(timetable[var], [1, 2, 3, 4])

    def test_all_csp_hard_constraints_satisfied(self) -> None:
        """Verify that the generated timetable satisfies 100% of hard constraints."""
        res = self.scheduler.solve_group_timetable()
        self.assertTrue(res.success)
        t = res.timetable

        # 1. Room / Resource Clashes (!=)
        self.assertNotEqual(t["G1"], t["G2"], "Clash: G1 != G2 violated")
        self.assertNotEqual(t["G1"], t["G4"], "Clash: G1 != G4 violated")
        self.assertNotEqual(t["G2"], t["G4"], "Clash: G2 != G4 violated")
        self.assertNotEqual(t["G3"], t["G5"], "Clash: G3 != G5 violated")
        self.assertNotEqual(t["G3"], t["G6"], "Clash: G3 != G6 violated")
        self.assertNotEqual(t["G5"], t["G6"], "Clash: G5 != G6 violated")

        # 2. Examiner Clash (!=): G1 != G3
        self.assertNotEqual(t["G1"], t["G3"], "Examiner Clash: G1 != G3 violated")

        # 3. Supervisor Clash (!=): G2 != G5
        self.assertNotEqual(t["G2"], t["G5"], "Supervisor Clash: G2 != G5 violated")

        # 4. Precedence Constraint (<): G4 < G3
        self.assertLess(t["G4"], t["G3"], f"Precedence violated: G4 ({t['G4']}) must be < G3 ({t['G3']})")

    def test_service_request_scheduling(self) -> None:
        """Ensure individual request scheduling allocates slot and room."""
        res = self.scheduler.schedule_service(
            request_id="REQ-101",
            preferred_slot=2,
            priority_level="urgent"
        )
        self.assertTrue(res.success)
        self.assertEqual(res.assigned_slot, 2)
        self.assertEqual(res.assigned_room, "AI_Lab")


if __name__ == "__main__":
    unittest.main()
