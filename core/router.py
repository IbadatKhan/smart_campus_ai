"""
Module: core.router
Description: Request Preprocessing, Schema Validation, 7-D Vector Extraction,
and Canonical Pipeline Routing for the 5 request types.
"""

from typing import List, Dict, Tuple, Optional
from core.models import UniversalRequest, PreprocessedRequest


class RequestPreprocessor:
    """
    Validates fields, normalizes casing/synonyms, and extracts
    the invariant 7-Dimensional numeric feature vector for the ANN.
    """

    ROLE_MAP: Dict[str, float] = {
        "student": 0.0,
        "instructor": 1.0,
        "staff": 2.0
    }

    CATEGORY_MAP: Dict[str, float] = {
        "ai_lab_support": 0.0,
        "viva_scheduling": 1.0,
        "access_request": 2.0,
        "maintenance": 3.0,
        "emergency_help": 4.0
    }

    VALID_REQUEST_TYPES: List[str] = [
        "Navigation_Only",
        "Eligibility_Check",
        "Booking_or_Scheduling",
        "Urgent_Service_Request",
        "Full_Service_Request"
    ]

    KNOWN_LANDMARKS: List[str] = [
        "Main_Gate", "Bus_Stop", "Medical_Center", "Hostel", "Parking",
        "Admin_Block", "Cafeteria", "Student_Services", "Library",
        "Science_Block", "Exam_Hall", "AI_Lab", "Seminar_Room"
    ]

    def validate(self, raw: UniversalRequest) -> Tuple[bool, Optional[str]]:
        """Validates all required fields and domain constraints."""
        if not raw.name or not raw.name.strip():
            return False, "Validation Error: User name cannot be empty."

        normalized_role = raw.role.strip().lower()
        if normalized_role not in self.ROLE_MAP:
            return False, f"Validation Error: Unknown role '{raw.role}'. Must be one of {list(self.ROLE_MAP.keys())}."

        if not (1 <= raw.severity <= 10):
            return False, f"Validation Error: Severity '{raw.severity}' must be an integer between 1 and 10."

        if not (1 <= raw.time_sensitivity <= 10):
            return False, f"Validation Error: TimeSensitivity '{raw.time_sensitivity}' must be between 1 and 10."

        if not (1 <= raw.crowd_level <= 10):
            return False, f"Validation Error: CrowdLevel '{raw.crowd_level}' must be between 1 and 10."

        # Validate landmarks if provided
        canonical_landmarks = {k.lower(): k for k in self.KNOWN_LANDMARKS}
        if raw.current_location and raw.current_location.strip().lower() not in canonical_landmarks:
            return False, f"Validation Error: Unknown location '{raw.current_location}'."

        if raw.destination and raw.destination.strip().lower() not in canonical_landmarks:
            return False, f"Validation Error: Unknown destination '{raw.destination}'."

        return True, None

    def normalize(self, raw: UniversalRequest) -> UniversalRequest:
        """Normalizes casing, trims whitespace, and canonicalizes landmarks."""
        canonical_landmarks = {k.lower(): k for k in self.KNOWN_LANDMARKS}
        curr = raw.current_location.strip().lower()
        dest = raw.destination.strip().lower()

        raw.name = raw.name.strip()
        raw.role = raw.role.strip().lower()
        raw.current_location = canonical_landmarks.get(curr, raw.current_location.strip())
        raw.destination = canonical_landmarks.get(dest, raw.destination.strip())
        return raw

    def extract_7d_vector(self, req: UniversalRequest) -> List[float]:
        """
        Extracts the fixed 7-Dimensional numerical feature vector:
        1. Role: student=0.0, instructor=1.0, staff=2.0
        2. Category: AI_Lab_Support=0.0 .. Emergency_Help=4.0
        3. Severity: 1.0 .. 10.0
        4. TimeSensitivity: 1.0 .. 10.0
        5. CrowdLevel: 1.0 .. 10.0
        6. Estimated Distance: float (default 5.0)
        7. Eligibility Claim: 1.0 if True else 0.0
        """
        role_val = self.ROLE_MAP.get(req.role.strip().lower(), 0.0)
        cat_key = req.category.strip().lower().replace(" ", "_")
        cat_val = self.CATEGORY_MAP.get(cat_key, 0.0)

        # Baseline distance heuristic placeholder
        dist_val = 5.0 if req.current_location != req.destination else 0.0
        elig_val = 1.0 if req.eligibility_claim else 0.0

        return [
            float(role_val),
            float(cat_val),
            float(req.severity),
            float(req.time_sensitivity),
            float(req.crowd_level),
            float(dist_val),
            float(elig_val)
        ]

    def process(self, raw: UniversalRequest) -> PreprocessedRequest:
        """Executes full validation, normalization, and vectorization."""
        valid, err = self.validate(raw)
        if not valid:
            return PreprocessedRequest(
                raw=raw,
                request_type=raw.request_type,
                feature_vector=[],
                is_valid=False,
                error_message=err
            )

        norm = self.normalize(raw)
        vector = self.extract_7d_vector(norm)
        return PreprocessedRequest(
            raw=norm,
            request_type=norm.request_type,
            feature_vector=vector,
            is_valid=True,
            error_message=None
        )


class RequestRouter:
    """
    Determines active computational filters for the 5 Canonical Pipelines.
    Bypasses unneeded modules dynamically to conserve computational resources.
    """

    PIPELINE_FILTERS: Dict[str, List[str]] = {
        "Navigation_Only": ["SEARCH"],
        "Eligibility_Check": ["LOGIC"],
        "Booking_or_Scheduling": ["LOGIC", "CSP"],
        "Urgent_Service_Request": ["ANN", "LOGIC", "CSP"],
        "Full_Service_Request": ["ANN", "LOGIC", "CSP", "SEARCH"]
    }

    def __init__(self, preprocessor: Optional[RequestPreprocessor] = None) -> None:
        self.preprocessor = preprocessor or RequestPreprocessor()

    def process(self, raw_req: UniversalRequest) -> PreprocessedRequest:
        """Delegates to preprocessor for validation and vectorization."""
        return self.preprocessor.process(raw_req)

    def get_active_filters(self, request_type: str) -> List[str]:
        """Returns list of active subsystem tags for the specified request type."""
        return self.PIPELINE_FILTERS.get(request_type, ["ANN", "LOGIC", "CSP", "SEARCH"])
