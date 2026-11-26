"""
Unit Tests for Neural Priority Engine & Pipeline Routing (Member 3)
Verifies Perceptron binary urgency, 7->4->3->4 Multiclass MLP forward pass,
Softmax normalization, and dynamic pipeline filter assignment.
"""

import unittest
from ai_engines.priority_ann.neural_engine import (
    SingleLayerPerceptron,
    MultilayerPerceptron,
    PriorityNeuralEngine
)
from core.router import RequestRouter, RequestPreprocessor
from core.models import UniversalRequest


class TestNeuralPriorityEngine(unittest.TestCase):
    """Test suite for Single-Layer Perceptron and Multiclass MLP."""

    def setUp(self) -> None:
        self.perceptron = SingleLayerPerceptron()
        self.mlp = MultilayerPerceptron()
        self.engine = PriorityNeuralEngine()

    def test_perceptron_urgency_decision(self) -> None:
        """High severity and time sensitivity must trigger 'urgent'."""
        # [role, category, severity, time_sens, crowd, dist, elig]
        urgent_vector = [0.0, 0.0, 9.0, 9.0, 6.0, 5.0, 1.0]
        not_urgent_vector = [0.0, 0.0, 1.0, 1.0, 1.0, 5.0, 1.0]

        self.assertEqual(self.perceptron.predict(urgent_vector), "urgent")
        self.assertEqual(self.perceptron.predict(not_urgent_vector), "not_urgent")

    def test_mlp_softmax_probability_distribution(self) -> None:
        """Softmax probabilities must sum to 1.0 across the 4 output classes."""
        test_vector = [0.0, 1.0, 7.0, 8.0, 5.0, 5.0, 1.0]
        pred_class, confidence, prob_dict = self.mlp.forward(test_vector)

        self.assertIn(pred_class, ["low", "normal", "high", "urgent"])
        self.assertEqual(len(prob_dict), 4)

        total_prob = sum(prob_dict.values())
        self.assertAlmostEqual(total_prob, 1.0, places=2)
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_mlp_priority_levels(self) -> None:
        """High stress vector yields urgent/high; low stress yields low/normal."""
        high_stress = [0.0, 4.0, 9.0, 9.0, 8.0, 5.0, 1.0]
        pred_high, _, _ = self.mlp.forward(high_stress)
        self.assertIn(pred_high, ["high", "urgent"])

        low_stress = [0.0, 0.0, 1.0, 1.0, 1.0, 5.0, 0.0]
        pred_low, _, _ = self.mlp.forward(low_stress)
        self.assertIn(pred_low, ["low", "normal"])

    def test_input_dimension_validation(self) -> None:
        """Invalid feature vector lengths must raise ValueError."""
        with self.assertRaises(ValueError):
            self.perceptron.predict([1.0, 2.0])
        with self.assertRaises(ValueError):
            self.mlp.forward([1.0, 2.0, 3.0])

    def test_priority_engine_returns_typed_priority_result(self) -> None:
        """PriorityNeuralEngine produces valid PriorityResult dataclass."""
        vector = [0.0, 0.0, 8.0, 9.0, 5.0, 5.0, 1.0]
        res = self.engine.classify_multiclass_priority(vector)

        self.assertIn(res.binary_priority, ["urgent", "not_urgent"])
        self.assertIn(res.final_priority, ["low", "normal", "high", "urgent"])
        self.assertGreater(res.confidence, 0.0)


class TestRouterPipelineIntegration(unittest.TestCase):
    """Test suite for the 5 canonical request pipelines."""

    def setUp(self) -> None:
        self.router = RequestRouter()
        self.preprocessor = RequestPreprocessor()

    def test_pipeline_filter_assignments(self) -> None:
        """Verify that router assigns expected filter chains for all 5 canonical pipelines."""
        self.assertEqual(
            self.router.get_active_filters("Navigation_Only"),
            ["SEARCH"]
        )
        self.assertEqual(
            self.router.get_active_filters("Eligibility_Check"),
            ["LOGIC"]
        )
        self.assertEqual(
            self.router.get_active_filters("Booking_or_Scheduling"),
            ["LOGIC", "CSP"]
        )
        self.assertEqual(
            self.router.get_active_filters("Urgent_Service_Request"),
            ["ANN", "LOGIC", "CSP"]
        )
        self.assertEqual(
            self.router.get_active_filters("Full_Service_Request"),
            ["ANN", "LOGIC", "CSP", "SEARCH"]
        )

    def test_preprocessor_7d_vector_extraction(self) -> None:
        """Verify that preprocessor extracts valid 7-D normalized vector from raw request."""
        req = UniversalRequest(
            request_id="REQ-TEST",
            name="Ali",
            role="student",
            request_type="Full_Service_Request",
            category="AI_Lab_Support",
            current_location="Hostel",
            destination="AI_Lab",
            preferred_slot=2,
            severity=8,
            time_sensitivity=9
        )
        preprocessed = self.preprocessor.process(req)
        self.assertTrue(preprocessed.is_valid)
        self.assertEqual(len(preprocessed.feature_vector), 7)
        # Severity is index 2, time_sensitivity is index 3
        self.assertEqual(preprocessed.feature_vector[2], 8.0)
        self.assertEqual(preprocessed.feature_vector[3], 9.0)


if __name__ == "__main__":
    unittest.main()
