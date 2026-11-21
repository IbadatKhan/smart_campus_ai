# Smart Campus AI Decision Support & Automation System
### Autonomous Multi-Agent Campus Operations, Resource Scheduling & Navigation Engine

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Strict%203--Tier%20Layered-orange.svg)](#system-architecture)
[![Design Patterns](https://img.shields.io/badge/Design%20Patterns-Two%20Master%20Facades%20%2B%20Ports%20%26%20Adapters-green.svg)](#system-architecture)
[![Testing](https://img.shields.io/badge/Tests-Passing%20(Unit%20%26%20Integration)-brightgreen.svg)](#verification--test-suite)

---

## 📌 Executive Summary

Modern university campuses require real-time, automated coordination across diverse operational domains: spatial pathfinding, facility access authorization, conflict-free timetable scheduling, and emergency triage. Typical university systems treat these problems in isolation, causing scheduling deadlocks, security authorization lags, and fragmented student navigation.

**Smart Campus AI** is an enterprise-grade decision support platform that unifies four distinct paradigms of Artificial Intelligence into a cohesive, decoupled **strict 3-Tier Layered Architecture**:
1. **Sub-symbolic Connectionist AI:** Perceptron & Multilayer Perceptron (MLP) for operational urgency and priority classification.
2. **Symbolic Knowledge Representation:** First-Order Logic (FOL) Knowledge Base with Forward-Chaining inference acting as an authorization gatekeeper.
3. **Combinatorial Optimization:** Constraint Satisfaction Problem (CSP) solver executing Backtracking with MRV, Degree, LCV, and Forward Checking.
4. **Heuristic State-Space Search:** A* spatial navigation with an admissible Euclidean heuristic alongside a 9-algorithm curriculum benchmark suite.

---

## 📐 System Architecture: Strict 3-Tier Layered with Two Master Facades

The system enforces complete decoupling between user interface components, business logic orchestration, and mathematical AI algorithms. Communication across layer boundaries occurs strictly through **Two Master Facades** and **Hexagonal Ports & Adapters**:

```
[ LAYER 1: Presentation Layer ]
  │  (presentation/cli_view.py, presentation/gui_advanced.py, main.py)
  │
  ▼  ◄── Boundary 1: Master Facade 1 (CoreFacade in core/core_facade.py)
[ LAYER 2: Orchestration & Business Logic (BLL) ]
  │  (core/router.py, core/models.py, core/contracts.py)
  │
  ▼  ◄── Boundary 2: Master Facade 2 (AIEngineFacade in ai_engines/engine_facade.py)
[ LAYER 3: Computational AI Engines Layer ]
  ┌───────────────────────┼───────────────────────┐
  ▼                       ▼                       ▼
[ NavigationEngine ]   [ NeuralEngine ]     [ ReasoningEngine ]
(ai_engines/navigation) (ai_engines/priority) (ai_engines/reasoning)
(implements IRouteFinder) (implements IPriority) (implements ILogic & IScheduler)
```

### Key Architectural Boundaries
* **Master Facade 1 (`CoreFacade` in `core/core_facade.py`):** Sits at Boundary 1. The Presentation layer interacts exclusively with `CoreFacade`. It coordinates the 5 canonical request workflows and enforces fail-fast circuit-breaker termination upon security rejection.
* **Master Facade 2 (`AIEngineFacade` in `ai_engines/engine_facade.py`):** Sits at Boundary 2. Encapsulates all algorithmic data structures (priority queues, heuristic evaluation, weight matrices, backtracking recursion), exposing clean, typed delegations to Layer 2.
* **Hexagonal Ports (`core/contracts.py`):** Pure abstract interfaces (`IRouteFinder`, `IPriorityClassifier`, `ILogicVerifier`, `IScheduler`) that define strict contracts, enabling 100% independent unit testing with zero subsystem blockers.

---

## 🧠 The 4 Computational AI Subsystems

The core intelligence is distributed across four autonomous computational engines:

```
                         ┌─────────────────────────────────────────────────────────┐
                         │               Smart Campus AI Engines                   │
                         └─────────────────────────────────────────────────────────┘
                                   │                   │                   │
         ┌─────────────────────────┴────────┐          │          ┌────────┴────────────────────────┐
         ▼                                  ▼          ▼          ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐   ┌──────────────────┐              ┌──────────────────┐
│  Spatial Search  │              │ Neural Priority  │   │   Symbolic KB    │              │  CSP Timetabler  │
│  Navigation AI   │              │  Connectionist   │   │ Security Gate    │              │  Combinatorial   │
├──────────────────┤              ├──────────────────┤   ├──────────────────┤              ├──────────────────┤
│ • A* Search      │              │ • 7-D Vector     │   │ • FOL Predicates │              │ • 6 Groups G1-G6 │
│ • Euclidean Heur │              │ • Perceptron     │   │ • Rules R1 - R4  │              │ • MRV Heuristic  │
│ • 9-Algo Suite   │              │ • 7-4-3-4 MLP    │   │ • Forward Chain  │              │ • Degree Tie-Brk │
│ • 13 Nodes / 19 E│              │ • ReLU & Softmax │   │ • Fail-Fast Gate │              │ • LCV & Fwd-Chk  │
└──────────────────┘              └──────────────────┘   └──────────────────┘              └──────────────────┘
```

### 1. Spatial Graph Navigation AI (`ai_engines/navigation/`)
* **Campus Topology:** 13 landmark nodes and 19 weighted/unweighted bidirectional edges representing campus pathways.
* **Admissible Heuristic:** Euclidean distance metric guarantee:
  $$h(n) = \sqrt{(x_n - x_{goal})^2 + (y_n - y_{goal})^2} \le h^*(n)$$
* **Search Algorithms Implemented:**
  1. Breadth-First Search (BFS) — Optimal for unweighted steps
  2. Depth-First Search (DFS)
  3. Uniform Cost Search (UCS / Dijkstra) — Optimal for weighted distance
  4. Depth-Limited Search (DLS)
  5. Iterative Deepening Search (IDS)
  6. Greedy Best-First Search
  7. **A\* Search (Optimal & Complete with Euclidean $h(n)$)**
  8. Recursive Best-First Search (RBFS)
  9. Bidirectional BFS

### 2. Connectionist Neural AI Urgency Engine (`ai_engines/priority_ann/`)
* **7-Dimensional Input Vector:** Standardized feature extraction encoding `[role_code, category_code, slot_idx, severity, time_sensitivity, crowd_level, access_history]`.
* **Single-Layer Perceptron:** Baseline binary linear classifier predicting `urgent` vs. `not_urgent`:
  $$z = \mathbf{w}^T \mathbf{x} + b, \quad \hat{y} = \text{step}(z)$$
* **Multiclass Multilayer Perceptron (MLP):** Fully connected 7 $\to$ 4 $\to$ 3 $\to$ 4 deep feedforward network utilizing hidden ReLU non-linearities and Softmax output distribution:
  $$\text{Softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}} \implies \{\text{low}, \text{normal}, \text{high}, \text{urgent}\}$$

### 3. Symbolic Knowledge AI & Security Gatekeeper (`ai_engines/reasoning/logic_kb.py`)
* **First-Order Logic Representation:** Working memory maintaining campus ground facts (`Student(x)`, `Completed(x, course)`, `HasRole(x, role)`).
* **Production Rules ($R_1 - R_4$):** Horn-clause security rules governing facility authorizations (e.g., prerequisite verification for AI Lab, administrative privileges for Exam Hall).
* **Forward Chaining Engine:** Applies Generalized Modus Ponens to evaluate eligibility. Acts as a **fail-fast circuit breaker** that instantly rejects unauthorized requests before expensive CSP or Search operations are invoked.

### 4. Combinatorial Constraint Satisfaction Timetabling (`ai_engines/reasoning/csp_scheduler.py`)
* **NP-Complete Viva Scheduling:** Schedules 6 presentation groups ($G_1$ to $G_6$) across available time slots without conflicts.
* **Active Constraints:**
  * Resource / Room Clashes: $G_3 \ne G_6$, $G_5 \ne G_6$
  * Examiner Clashes: $G_1 \ne G_3$
  * Supervisor Clashes: $G_2 \ne G_5$
  * Precedence Constraint: $G_4 < G_3$
* **Heuristics & Pruning:** Backtracking solver enhanced with:
  * **MRV (Minimum Remaining Values):** Selects variable with the tightest remaining legal domain.
  * **Degree Heuristic:** Breaks ties by choosing the variable involved in the greatest number of constraints.
  * **LCV (Least Constraining Value):** Prioritizes values that rule out the fewest choices for neighboring variables.
  * **Forward Checking:** Prunes inconsistent values from neighbor domains at each assignment.

---

## ⚡ The 5 Canonical Request Pipelines

Requests are dynamically routed through customized filter chains:

| Pipeline | Request Type | Active Computational Filters | Operational Purpose |
| :---: | :--- | :--- | :--- |
| **P1** | `Navigation_Only` | Preprocessing $\to$ Spatial Search | Campus navigation between landmarks |
| **P2** | `Eligibility_Check` | Preprocessing $\to$ FOL Knowledge Gatekeeper | Course prerequisite & role verification |
| **P3** | `Booking_or_Scheduling` | Preprocessing $\to$ FOL Logic $\to$ CSP Scheduler | Conflict-free room and viva slot reservation |
| **P4** | `Urgent_Service_Request` | Preprocessing $\to$ Neural ANN $\to$ FOL Logic $\to$ CSP $\to$ Spatial Search | High-priority lab assistance with routing |
| **P5** | `Full_Service_Request` | Preprocessing $\to$ ANN Urgency $\to$ FOL Gatekeeper $\to$ CSP $\to$ A\* Navigation | End-to-end multi-agent operational request |

---

## 💻 Code Usage Examples

### 1. Programmatic Python API
The system can be integrated programmatically by interacting solely through `CoreFacade`:

```python
from core.models import UniversalRequest
from core.router import RequestRouter
from core.core_facade import CoreFacade
from ai_engines.engine_facade import AIEngineFacade

# 1. Initialize the 3-Tier Layered Architecture via Master Facades
ai_engine = AIEngineFacade()
router = RequestRouter()
campus_system = CoreFacade(router=router, ai_facade=ai_engine)

# 2. Formulate a multi-agent service request
request = UniversalRequest(
    request_id="REQ-4091",
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

# 3. Execute request through the orchestrated pipeline
response = campus_system.execute(request)

# 4. Inspect aggregated decisions
print(f"System Decision : {response.decision.upper()}")
print(f"Assigned Room   : {response.assignment.assigned_room} (Slot {response.assignment.assigned_slot})")
print(f"Navigation Path : {' -> '.join(response.route.path)}")
print(f"Total Distance  : {response.route.cost:.2f} km")
```

### 2. Interactive Terminal CLI
You can also launch the fully interactive terminal console:

```bash
python main.py
``

Or launch the graphical campus map visualizer (GUI):
``ash
python main.py --gui
```

Sample output rendering the aggregated ASCII Decision Card:

```text
======================================================================
           SMART CAMPUS AI - UNIFIED DECISION CARD
======================================================================
  Request ID    : REQ-4091
  Status        : ACCEPTED
  Message       : Request successfully processed. Assigned AI_Lab at slot 2.

[STAGE 1: NEURAL PRIORITY ESTIMATION (ANN)]
  • Binary Urgency      : urgent
  • Multi-Class Priority: urgent (Confidence: 89.4%)

[STAGE 2: SECURITY GATEKEEPER (FIRST-ORDER LOGIC)]
  • Access Entitlement  : ALLOWED
  • Justification       : Student verified; course prerequisites satisfied.

[STAGE 3: RESOURCE ALLOCATION (CSP TIMETABLER)]
  • Assigned Facility   : AI_Lab
  • Assigned Slot       : Slot 2 (10:00 AM - 11:30 AM)
  • Conflict Status     : Conflict-free (MRV + Degree solved)

[STAGE 4: SPATIAL NAVIGATION (A* EUCLIDEAN SEARCH)]
  • Path                : Hostel -> Cafeteria -> Science_Block -> AI_Lab
  • Total Cost          : 6.00 km
  • Steps               : 3 hops
======================================================================
```

---

## 📁 Repository Structure

```
smart_campus_ai/
│
├── main.py                             # Root application entrypoint (CLI runner)
├── requirements.txt                    # Project dependencies (numpy, pytest)
├── README.md                           # Master project documentation
├── AI_PROJECT_SRS.md                   # System Requirements Specification
├── AI_PROJECT_ARCHITECTURE.md          # Full Architecture & UML Design Blueprint
│
├── presentation/                       # LAYER 1: PRESENTATION LAYER
│   ├── __init__.py
│   ├── cli_view.py                     # Interactive Campus CLI & Scenario Suite
│   └── gui_advanced.py                 # Advanced Graphical Tkinter Window
│
├── core/                               # LAYER 2: ORCHESTRATION & BLL LAYER
│   ├── __init__.py
│   ├── models.py                       # Pure Data Transfer Objects (DTOs)
│   ├── contracts.py                    # Port Interfaces (IRouteFinder, etc.)
│   ├── router.py                       # Request Preprocessor & Dynamic Router
│   └── core_facade.py                  # MASTER FACADE 1: CoreFacade
│
├── ai_engines/                         # LAYER 3: COMPUTATIONAL AI ENGINES
│   ├── __init__.py
│   ├── engine_facade.py                # MASTER FACADE 2: AIEngineFacade
│   │
│   ├── navigation/                     # Spatial Graph AI Subsystem
│   │   ├── __init__.py
│   │   ├── campus_graph.py             # 13 nodes, coordinates, Euclidean heuristic
│   │   └── search_engine.py            # A*, BFS, UCS, and 9-algorithm benchmark suite
│   │
│   ├── reasoning/                      # Symbolic Logic & Constraint AI Subsystem
│   │   ├── __init__.py
│   │   ├── logic_kb.py                 # FOL KB, Rules R1-R4, Forward Chaining Gatekeeper
│   │   └── csp_scheduler.py            # 6-group Backtracking CSP (MRV, Degree, LCV, FC)
│   │
│   └── priority_ann/                   # Connectionist Neural AI Subsystem
│       ├── __init__.py
│       └── neural_engine.py            # Single-layer Perceptron + Multiclass MLP
│
└── tests/                              # VERIFICATION LAYER (Unit & Integration Tests)
    ├── __init__.py
    ├── test_navigation.py              # Graph topology and search tests
    ├── test_reasoning.py               # FOL rule deduction and CSP tests
    └── test_ann_pipeline.py            # Neural classification and pipeline tests
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
* Python 3.10 or higher
* Git

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/IbadatKhan/smart_campus_ai.git
cd smart_campus_ai

# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
Launch the interactive command-line interface (CLI):
```bash
python main.py
```

Or launch the graphical campus map visualizer (GUI):
```bash
python main.py --gui
```

### 4. Run the Test Suite
```bash
pytest tests/ -v
```


