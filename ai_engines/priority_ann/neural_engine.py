"""
Neural Network Priority Estimation Module
Implements Single-Layer Perceptron (binary baseline) and 7 -> 4 -> 3 -> 4
Multilayer Perceptron (MLP) with ReLU hidden units and Softmax output.
"""

import math
from typing import Dict, List, Tuple, Optional
from core.contracts import IPriorityClassifier
from core.models import PriorityResult


class SingleLayerPerceptron:
    """
    Single-layer binary urgency baseline classifier.
    Linear threshold model: z = w^T * x + b; step(z) -> urgent / not_urgent.
    Features: [role, category, severity, time_sensitivity, crowd, dist, elig]
    """

    def __init__(self, weights: Optional[List[float]] = None, bias: float = -6.5) -> None:
        # Pre-calibrated weights emphasizing severity (x2) and time sensitivity (x3)
        self.weights: List[float] = weights or [0.1, 0.2, 0.6, 0.7, 0.2, 0.0, 0.0]
        self.bias: float = bias

    def step_function(self, z: float) -> int:
        """Heaviside step function: 1 if z >= 0 else 0."""
        return 1 if z >= 0.0 else 0

    def predict(self, feature_vector: List[float]) -> str:
        """Returns 'urgent' or 'not_urgent' based on linear threshold."""
        if len(feature_vector) != len(self.weights):
            raise ValueError(
                f"Feature vector length ({len(feature_vector)}) does not match "
                f"expected input dimension ({len(self.weights)})."
            )

        z = sum(w * x for w, x in zip(self.weights, feature_vector)) + self.bias
        return "urgent" if self.step_function(z) == 1 else "not_urgent"


class MultilayerPerceptron:
    """
    Operational 4-class priority classifier: 7 -> 4 -> 3 -> 4 feedforward network.
    Hidden layers use ReLU non-linearities; output layer uses Softmax distribution.
    Classes: ['low', 'normal', 'high', 'urgent']
    """

    CLASSES: List[str] = ["low", "normal", "high", "urgent"]

    def __init__(self) -> None:
        # Layer 1: 7 inputs -> 4 hidden neurons
        self.w1: List[List[float]] = [
            [ 0.0,  0.0,  0.0,  0.0],  # Role
            [ 0.0,  0.0,  0.1,  0.2],  # Category
            [-0.5, -0.1,  0.3,  0.5],  # Severity
            [-0.5, -0.1,  0.3,  0.5],  # Time Sensitivity
            [-0.1,  0.0,  0.1,  0.1],  # Crowd Level
            [ 0.0,  0.0,  0.0,  0.0],  # Distance
            [ 0.0,  0.0,  0.0,  0.0],  # Eligibility
        ]
        self.b1: List[float] = [4.0, 1.5, -2.5, -7.0]

        # Layer 2: 4 hidden -> 3 hidden neurons
        self.w2: List[List[float]] = [
            [ 1.5,  0.0, -0.5],
            [ 0.0,  1.5,  0.0],
            [-0.5,  0.5,  1.2],
            [-1.0, -0.5,  2.0],
        ]
        self.b2: List[float] = [0.0, 0.0, -0.5]

        # Layer 3: 3 hidden -> 4 output classes [low, normal, high, urgent]
        self.w3: List[List[float]] = [
            [ 2.5, -0.5, -1.0, -2.0],
            [-0.5,  2.0,  0.5, -1.5],
            [-2.0, -0.5,  1.8,  3.0],
        ]
        self.b3: List[float] = [1.0, 0.5, 0.0, -1.0]

    @staticmethod
    def relu(z: float) -> float:
        """Rectified Linear Unit activation."""
        return max(0.0, z)

    @staticmethod
    def softmax(logits: List[float]) -> List[float]:
        """Numerically stable Softmax probability distribution."""
        max_logit = max(logits)
        exp_vals = [math.exp(v - max_logit) for v in logits]
        total_exp = sum(exp_vals)
        return [v / total_exp for v in exp_vals]

    def forward(self, x: List[float]) -> Tuple[str, float, Dict[str, float]]:
        """
        Executes full feedforward pass:
        Returns (predicted_class, confidence_score, probabilities_dict).
        """
        if len(x) != 7:
            raise ValueError(f"Expected 7-D feature vector, received length {len(x)}.")

        # Hidden Layer 1: z1 = W1^T * x + b1; a1 = ReLU(z1)
        a1: List[float] = []
        for j in range(4):
            z = sum(x[i] * self.w1[i][j] for i in range(7)) + self.b1[j]
            a1.append(self.relu(z))

        # Hidden Layer 2: z2 = W2^T * a1 + b2; a2 = ReLU(z2)
        a2: List[float] = []
        for j in range(3):
            z = sum(a1[i] * self.w2[i][j] for i in range(4)) + self.b2[j]
            a2.append(self.relu(z))

        # Output Layer: z3 = W3^T * a2 + b3; probs = Softmax(z3)
        logits: List[float] = []
        for j in range(4):
            z = sum(a2[i] * self.w3[i][j] for i in range(3)) + self.b3[j]
            logits.append(z)

        probs = self.softmax(logits)
        prob_dict = {cls_name: round(p, 4) for cls_name, p in zip(self.CLASSES, probs)}

        # Argmax selection
        max_idx = max(range(len(probs)), key=lambda i: probs[i])
        predicted_class = self.CLASSES[max_idx]
        confidence = round(probs[max_idx], 4)

        return predicted_class, confidence, prob_dict


class PriorityNeuralEngine(IPriorityClassifier):
    """
    Neural urgency and priority prediction coordinator implementing IPriorityClassifier.
    Orchestrates both baseline Perceptron and operational Multiclass MLP.
    """

    def __init__(self) -> None:
        self.perceptron = SingleLayerPerceptron()
        self.mlp = MultilayerPerceptron()

    def classify_binary_urgency(self, feature_vector: List[float]) -> str:
        """Evaluates 7-D vector via Perceptron returning 'urgent' or 'not_urgent'."""
        return self.perceptron.predict(feature_vector)

    def classify_multiclass_priority(self, feature_vector: List[float]) -> PriorityResult:
        """Evaluates 7-D vector via MLP returning operational class and confidence."""
        binary_urgency = self.classify_binary_urgency(feature_vector)
        pred_class, confidence, _ = self.mlp.forward(feature_vector)

        return PriorityResult(
            binary_priority=binary_urgency,
            final_priority=pred_class,
            confidence=confidence
        )
