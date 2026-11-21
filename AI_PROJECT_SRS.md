# Software Requirements Specification (SRS)
## Smart Campus AI Decision Support and Automation System
**Project Title:** Smart Campus AI Decision Support and Automation System  
**Course:** AL2002 – Artificial Intelligence – Lab (Fall 2026)  
**Institution:** National University of Computer & Emerging Sciences (FAST-NUCES)  
**Standard:** Aligned with IEEE Std 830-1998 / ISO/IEC/IEEE 29148  
**Scope:** Complete System Requirements ("WHAT to Build")  
**Notice:** This document is 100% self-contained. A developer or evaluator reading this document does NOT need to refer to any original PDF, handout, or diagram image. All nodes, coordinates, weights, rules, constraints, encodings, and formulas are fully specified herein.

---

## Table of Contents
1. [Introduction & Project Scope](#1-introduction--project-scope)
2. [General System Constraints & Philosophy](#2-general-system-constraints--philosophy)
3. [User Roles & Authorization Matrix](#3-user-roles--authorization-matrix)
4. [Campus Topological Map Specification (Search Module Domain)](#4-campus-topological-map-specification-search-module-domain)
5. [First-Order Logic (FOL) Knowledge Base Specification (Symbolic Reasoning Domain)](#5-first-order-logic-fol-knowledge-base-specification-symbolic-reasoning-domain)
6. [Constraint Satisfaction Problem (CSP) Timetable Specification (Constraint Domain)](#6-constraint-satisfaction-problem-csp-timetable-specification-constraint-domain)
7. [Artificial Neural Network (ANN) Priority Estimation Specification (Machine Learning Domain)](#7-artificial-neural-network-ann-priority-estimation-specification-machine-learning-domain)
8. [The Five (5) Canonical Request Types & Execution Pipelines](#8-the-five-5-canonical-request-types--execution-pipelines)
9. [Standard Input / Output Data Formats & Schemas](#9-standard-input--output-data-formats--schemas)
10. [Error Handling & Rejection Protocol](#10-error-handling--rejection-protocol)
11. [Academic Comparison & Benchmark Requirements](#11-academic-comparison--benchmark-requirements)
12. [Evaluation Rubrics & Submission Criteria](#12-evaluation-rubrics--submission-criteria)

---

# 1. Introduction & Project Scope

### 1.1 Purpose
This document defines the complete functional and non-functional requirements for the **Smart Campus AI Decision Support and Automation System**. The platform acts as an intelligent service desk for a university campus, accepting structured requests from students, faculty, and staff, routing them through specialized AI sub-engines, and returning explainable, unified decisions.

### 1.2 Scope of the AI System
The system integrates four distinct pillars of Artificial Intelligence:
1. **Machine Learning / Neural Networks:** Urgency and multi-level priority prediction using a Single-Layer Perceptron (baseline) and a Multilayer Perceptron (operational).
2. **Symbolic Logic & Knowledge Representation:** First-Order Logic (FOL) forward-chaining deduction serving as an authoritative **Security Gatekeeper** verifying prerequisite eligibility and access rights.
3. **Constraint Satisfaction Problems (CSP):** Backtracking search with MRV, Degree Heuristic, LCV, and Forward Checking for conflict-free examination slot and room allocation across 6 student groups.
4. **Spatial Graph Search:** Route planning over a 13-landmark campus graph using BFS (unweighted), A* with Euclidean distance heuristic (weighted), UCS (fallback), and a benchmark suite of 6 additional lab search algorithms.

---

# 2. General System Constraints & Philosophy

### 2.1 Core Invariants
1. **Structured Input Only:** The system shall NOT accept ambiguous free-text NLP paragraphs. All user input is captured via a step-by-step structured CLI form asking for explicit, typed fields.
2. **ANN is an Estimator, NOT a Decision-Maker:** ANN output is strictly numerical priority/urgency estimation. The ANN shall NEVER grant permissions, enroll students, or bypass logical verification.
3. **Logic KB is the Gatekeeper:** For any request requiring resource allocation or full service, the FOL Knowledge Base must verify eligibility *before* CSP or Search runs. If logic verification fails, processing terminates immediately with an explanatory deduction trace.
4. **Pipeline Separation:** Modules execute strictly on demand. Unneeded modules are bypassed (e.g., a routing request never triggers the ANN or CSP).
5. **Deterministic Data Contracts:** Modules communicate using standardized Python dictionaries/dataclasses conforming to fixed schemas.

---

# 3. User Roles & Authorization Matrix

The system recognizes three primary campus user roles:
1. **`student`**: Enrolled learners. Can request navigation, check course eligibility, request lab support slots, and participate in presentation schedules.
2. **`instructor`**: Academic faculty. Authorized for lab usage, course assignment, exam scheduling, and emergency overrides.
3. **`staff`**: Administrative and maintenance personnel. Authorized for facility access, maintenance booking, and general navigation.

### Role Authorization Rules
* Students may access `AI_Lab` only if enrolled in the corresponding course (`AI`) and prerequisite conditions (`Completed(ProgrammingFundamentals)`) are satisfied.
* Instructors may use university laboratories if they teach the relevant course.
* High severity requests ($severity \ge 8$) require priority estimation via the ANN module.

---

# 4. Campus Topological Map Specification (Search Module Domain)

The campus physical layout is modeled as a connected graph of **13 landmarks** located on a 2D Cartesian coordinate plane.

### 4.1 Campus Landmarks & Physical $(x, y)$ Coordinates
Coordinates are used to compute the straight-line Euclidean distance heuristic:
$$h(n) = \sqrt{(x_n - x_{\text{goal}})^2 + (y_n - y_{\text{goal}})^2}$$

| Node ID | Landmark Name | X Coordinate | Y Coordinate | Description |
| :---: | :--- | :---: | :---: | :--- |
| **N1** | `Main_Gate` | `0.0` | `4.0` | Campus primary vehicle & pedestrian entrance |
| **N2** | `Bus_Stop` | `0.0` | `1.0` | Shuttle and public transit stop |
| **N3** | `Medical_Center` | `1.0` | `1.0` | First-aid and health dispensary |
| **N4** | `Hostel` | `2.0` | `0.0` | Student residential dormitories |
| **N5** | `Parking` | `2.0` | `4.0` | Central vehicle parking lot |
| **N6** | `Admin_Block` | `3.0` | `5.0` | Dean, Registrar, and Administrative offices |
| **N7** | `Cafeteria` | `4.0` | `1.0` | Central dining hall and student hub |
| **N8** | `Student_Services` | `6.0` | `5.0` | Academic advising, financial aid, desks |
| **N9** | `Library` | `6.0` | `2.0` | Central library and reading rooms |
| **N10** | `Science_Block` | `7.0` | `1.0` | Natural sciences, physics, chemistry labs |
| **N11** | `Exam_Hall` | `8.0` | `5.0` | Auditorium and formal examination center |
| **N12** | `AI_Lab` | `9.0` | `2.0` | Advanced computing & AI project laboratory |
| **N13** | `Seminar_Room` | `10.0` | `4.0` | Presentation and viva conference hall |

### 4.2 Graph Topology & Edge Specifications
The campus graph supports two operating modes:
* **Unweighted Graph:** Every edge represents a uniform hop count of $1.0$.
* **Weighted Graph:** Every edge represents walking cost/distance in minutes/distance units.

All edges are bidirectional (undirected). The complete set of **19 edges** is:

| Edge # | Node A | Node B | Weighted Cost | Unweighted Cost |
| :---: | :--- | :--- | :---: | :---: |
| 1 | `Main_Gate` | `Bus_Stop` | `1.0` | `1.0` |
| 2 | `Main_Gate` | `Parking` | `2.0` | `1.0` |
| 3 | `Main_Gate` | `Admin_Block` | `4.0` | `1.0` |
| 4 | `Main_Gate` | `Hostel` | `5.0` | `1.0` |
| 5 | `Bus_Stop` | `Parking` | `2.0` | `1.0` |
| 6 | `Bus_Stop` | `Medical_Center` | `2.0` | `1.0` |
| 7 | `Medical_Center` | `Hostel` | `3.0` | `1.0` |
| 8 | `Hostel` | `Cafeteria` | `2.0` | `1.0` |
| 9 | `Parking` | `Science_Block` | `3.0` | `1.0` |
| 10 | `Admin_Block` | `Student_Services` | `1.0` | `1.0` |
| 11 | `Admin_Block` | `Exam_Hall` | `2.0` | `1.0` |
| 12 | `Cafeteria` | `Library` | `2.0` | `1.0` |
| 13 | `Cafeteria` | `Science_Block` | `3.0` | `1.0` |
| 14 | `Student_Services` | `Library` | `2.0` | `1.0` |
| 15 | `Library` | `AI_Lab` | `3.0` | `1.0` |
| 16 | `Science_Block` | `Exam_Hall` | `3.0` | `1.0` |
| 17 | `Science_Block` | `AI_Lab` | `1.0` | `1.0` |
| 18 | `Science_Block` | `Seminar_Room` | `2.0` | `1.0` |
| 19 | `Exam_Hall` | `Seminar_Room` | `1.0` | `1.0` |

### 4.3 Search Algorithm Operational Policy
* **Unweighted Routing Requests:** The system SHALL use **Breadth-First Search (BFS)** to guarantee the minimal hop count path.
* **Weighted Routing Requests with Heuristic:** The system SHALL use **A\* Search** with the Euclidean distance heuristic.
* **Weighted Routing Requests without Heuristic:** The system SHALL use **Uniform-Cost Search (UCS)** as the optimal least-cost fallback.

---

# 5. First-Order Logic (FOL) Knowledge Base Specification (Symbolic Reasoning Domain)

The Knowledge Base serves as the **Security Gatekeeper**. It enforces university policies, course eligibility, and access authorization.

### 5.1 Predicates & Semantics
* `Student(x)`: $x$ is a registered student.
* `Instructor(x, c)`: $x$ is an authorized instructor for course $c$.
* `Teaches(x, c)`: $x$ conducts lectures for course $c$.
* `Completed(x, c)`: Person $x$ has successfully completed course $c$.
* `Enrolled(x, c)`: Person $x$ is actively enrolled in course $c$.
* `Eligible(x, c)`: Person $x$ satisfies all prerequisites to attend or request services for course $c$.
* `UsesLab(x, lab)`: Person $x$ is authorized to enter and utilize room $lab$.

### 5.2 Initial Fact Base (Ground Atoms)
The system initializes with the following facts:
1. `Student(Ali)`
2. `Student(Sara)`
3. `Completed(Ali, ProgrammingFundamentals)`
4. `Teaches(DrKhan, AI)`
5. `Enrolled(Ali, AI)`

*(Note: Sara has NOT completed ProgrammingFundamentals, providing an explicit test case for gatekeeper rejection).*

### 5.3 Implication Rules
* **Rule $R_1$ (Prerequisite Satisfaction):**
  $$\forall x \, [\text{Student}(x) \land \text{Completed}(x, \text{ProgrammingFundamentals}) \implies \text{Eligible}(x, \text{AI})]$$
* **Rule $R_2$ (Faculty Authorization):**
  $$\forall x \, [\text{Teaches}(x, \text{AI}) \implies \text{Instructor}(x, \text{AI})]$$
* **Rule $R_3$ (Student Lab Access):**
  $$\forall x \, [\text{Enrolled}(x, \text{AI}) \implies \text{UsesLab}(x, \text{Lab1})]$$
* **Rule $R_4$ (Instructor Lab Access):**
  $$\forall x \, [\text{Instructor}(x, \text{AI}) \implies \text{UsesLab}(x, \text{Lab1})]$$

### 5.4 Inference Engine Requirements
* The engine must implement **Forward Chaining** applying Modus Ponens iteratively.
* On completion, it must return:
  1. `allowed`: Boolean (`True` if goal atom is derived, `False` otherwise).
  2. `entailed`: Boolean.
  3. `explanation`: An ordered list of strings showing the exact rule substitutions and deductions performed.

---

# 6. Constraint Satisfaction Problem (CSP) Timetable Specification (Constraint Domain)

The CSP module is responsible for scheduling final presentation vivas for 6 student project groups across available presentation slots without conflicts.

### 6.1 Variables
The set of variables represents the 6 student groups:
$$X = \{G_1, G_2, G_3, G_4, G_5, G_6\}$$

### 6.2 Domains
Each group must be assigned to one time slot from the domain:
$$D(G_i) = \{1, 2, 3, 4\} \quad \forall G_i \in X$$
*(Where 1 = Slot 1, 2 = Slot 2, 3 = Slot 3, 4 = Slot 4).*

### 6.3 Constraints
The CSP must strictly enforce the following hard constraints:

1. **Resource & Room Clashes ($\ne$):** Groups sharing the same presentation venue cannot present simultaneously:
   * $G_1 \ne G_2$
   * $G_1 \ne G_4$
   * $G_2 \ne G_4$
   * $G_3 \ne G_5$
   * $G_3 \ne G_6$
   * $G_5 \ne G_6$
2. **Examiner Conflict ($\ne$):** The external examiner sits on panels for both $G_1$ and $G_3$:
   * $G_1 \ne G_3$
3. **Supervisor Conflict ($\ne$):** The lead supervisor advises both $G_2$ and $G_5$:
   * $G_2 \ne G_5$
4. **Temporal Precedence ($<$):** Group $G_4$ presents an introductory prerequisite module and MUST present strictly before Group $G_3$:
   * $G_4 < G_3$

### 6.4 Algorithmic Solver Requirements
The backtracking search solver MUST implement the following classical AI heuristics:
* **Minimum Remaining Values (MRV):** Choose the unassigned variable with the fewest legal values remaining in its domain.
* **Degree Heuristic (DH):** Break ties in MRV by selecting the variable with the maximum number of constraints on remaining unassigned variables.
* **Least Constraining Value (LCV):** Order domain values by the number of choices ruled out for neighboring variables (pick value that leaves maximal options for others).
* **Forward Checking (FC):** When a variable $X$ is assigned value $v$, immediately prune $v$ from domains of all unassigned variables connected to $X$ by a constraint. If any domain becomes empty, backtrack immediately.

---

# 7. Artificial Neural Network (ANN) Priority Estimation Specification (Machine Learning Domain)

The ANN module estimates request urgency and priority from structured numerical features.

### 7.1 Fixed 7-Dimensional Input Feature Vector Order
Features MUST be extracted in this exact, invariant sequence:
1. `Role`: Categorical encoding.
2. `RequestType`: Categorical encoding.
3. `Severity`: Integer scale $1 \dots 10$.
4. `TimeSensitivity`: Integer scale $1 \dots 10$.
5. `CrowdLevel`: Integer scale $1 \dots 10$.
6. `Distance`: Float value (campus distance estimate).
7. `Eligibility`: Boolean integer ($1 = \text{True}, 0 = \text{False}$).

### 7.2 Numerical Encodings
* **Role Encoding:**
  * `student`: $0$
  * `instructor`: $1$
  * `staff`: $2$
* **Request Type / Category Encoding:**
  * `AI_Lab_Support`: $0$
  * `Viva_Scheduling`: $1$
  * `Access_Request`: $2$
  * `Maintenance`: $3$
  * `Emergency_Help`: $4$

### 7.3 Model 1: Single-Layer Perceptron (Binary Baseline)
* **Objective:** Predict binary urgency (`not_urgent` vs `urgent`).
* **Mathematical Model:**
  $$\hat{y} = \begin{cases} 1 & \text{if } \sum_{i=1}^{7} w_i x_i + b \ge 0 \\ 0 & \text{otherwise} \end{cases}$$
* **Classes:** $0 = \text{"not\_urgent"}$, $1 = \text{"urgent"}$.
* **Role:** Baseline comparison model for reports and vivas.

### 7.4 Model 2: Multilayer Perceptron (MLP - Operational Multiclass)
* **Objective:** Predict fine-grained operational priority over 4 classes: `["low", "normal", "high", "urgent"]`.
* **Architecture:** $7 \to 4 \to 3 \to 4$:
  * **Input Layer:** 7 features ($x_1 \dots x_7$) + bias.
  * **Hidden Layer 1:** 4 neurons with ReLU activation: $\text{ReLU}(z) = \max(0, z)$.
  * **Hidden Layer 2:** 3 neurons with ReLU activation.
  * **Output Layer:** 4 neurons with Softmax activation:
    $$\text{Softmax}(z_k) = \frac{e^{z_k}}{\sum_{j=1}^{4} e^{z_j}}$$
* **Output:** Returns class with highest probability along with numeric confidence score $\in [0.0, 1.0]$.
* **Operational Rule:** The CSP Scheduler consumes the **MLP final priority** for all scheduling decisions.

---

# 8. The Five (5) Canonical Request Types & Execution Pipelines

Every request submitted to the system maps to one of five distinct pipelines.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 5 CANONICAL AI PIPELINES                              │
├──────────────────────────┬─────────────────────────────────────────────────────────────┤
│ 1. Navigation_Only       │ CLI -> Preprocessing -> Router -> Search -> Final Response  │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 2. Eligibility_Check     │ CLI -> Preprocessing -> Router -> Logic KB -> Final Response│
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 3. Booking_or_Scheduling │ CLI -> Preproc -> Router -> Logic KB -> CSP -> [Search?]    │
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 4. Urgent_Service_Request│ CLI -> Preproc -> Router -> ANN -> Logic -> CSP -> [Search?]│
├──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ 5. Full_Service_Request  │ CLI -> Preproc -> Router -> ANN -> Logic -> CSP -> Search   │
└──────────────────────────┴─────────────────────────────────────────────────────────────┘
```

### 8.1 Request Type 1: `Navigation_Only`
* **Purpose:** Point-to-point campus route guidance.
* **CLI Required Fields:** `name`, `role`, `current_location`, `destination`.
* **Pipeline:** Preprocessing $\to$ Router $\to$ **Search Module** $\to$ Final Response.
* **Bypassed Modules:** ANN, Logic KB, CSP.

### 8.2 Request Type 2: `Eligibility_Check`
* **Purpose:** Query whether a student or instructor is authorized or satisfies prerequisites.
* **CLI Required Fields:** `name`, `role`, `query` (e.g., `"UsesLab(DrKhan, Lab1)"` or `"Eligible(Ali, AI)"`).
* **Pipeline:** Preprocessing $\to$ Router $\to$ **Logic / KB Module** $\to$ Final Response.
* **Bypassed Modules:** ANN, CSP, Search.

### 8.3 Request Type 3: `Booking_or_Scheduling`
* **Purpose:** Reserve a lab slot or schedule a group presentation.
* **CLI Required Fields:** `name`, `role`, `category`, `preferred_slot`, optional `current_location`.
* **Pipeline:** Preprocessing $\to$ Router $\to$ **Logic KB** $\to$ *Allowed?*
  * If Allowed = `False` $\to$ Rejection Handler $\to$ Final Response.
  * If Allowed = `True` $\to$ **CSP Scheduler** $\to$ (Search if route needed) $\to$ Final Response.
* **Bypassed Modules:** ANN.

### 8.4 Request Type 4: `Urgent_Service_Request`
* **Purpose:** Time-critical campus assistance requiring priority estimation before scheduling.
* **CLI Required Fields:** `name`, `role`, `category`, `current_location`, `severity`, `time_sensitivity`, `crowd_level`, `preferred_slot`.
* **Pipeline:** Preprocessing $\to$ Router $\to$ **ANN Priority** $\to$ **Logic KB** $\to$ *Allowed?*
  * If Allowed = `False` $\to$ Rejection Handler $\to$ Final Response.
  * If Allowed = `True` $\to$ **CSP Scheduler** $\to$ (Optional Search) $\to$ Final Response.

### 8.5 Request Type 5: `Full_Service_Request` (Flagship Pipeline)
* **Purpose:** Complete campus workflow: priority prediction, eligibility verification, conflict-free slot booking, and pathfinding to the assigned room.
* **CLI Required Fields:** `name`, `role`, `category`, `current_location`, `preferred_slot`, `severity`, `time_sensitivity`, `crowd_level`, `description_note`.
* **Pipeline:** Preprocessing $\to$ Router $\to$ **ANN Priority** $\to$ **Logic KB** $\to$ *Allowed?*
  * If Allowed = `False` $\to$ Rejection Handler $\to$ Final Response.
  * If Allowed = `True` $\to$ **CSP Scheduler** $\to$ **Search Module** $\to$ Final Response.
* **Demonstration Note:** Exercises all 4 AI engines in a single execution.

---

# 9. Standard Input / Output Data Formats & Schemas

### 9.1 Universal Input Schema (CLI Form)
```json
{
  "request_id": "REQ205",
  "name": "Ali",
  "role": "student",
  "request_type": "Full_Service_Request",
  "category": "AI_Lab_Support",
  "current_location": "Hostel",
  "destination": "",
  "preferred_slot": 2,
  "severity": 8,
  "time_sensitivity": 9,
  "crowd_level": 5,
  "group_id": "",
  "query": "",
  "eligibility_claim": true,
  "description_note": "Need urgent help before practical evaluation."
}
```

### 9.2 Universal Output Schema (Final Response)
```json
{
  "request_id": "REQ205",
  "decision": "accepted",
  "priority": {
    "binary_priority": "urgent",
    "final_priority": "high",
    "confidence": 0.87
  },
  "eligibility": {
    "allowed": true,
    "explanation": "Ali has completed ProgrammingFundamentals and is enrolled in AI."
  },
  "assignment": {
    "assigned_room": "AI_Lab",
    "assigned_slot": 3,
    "destination": "AI_Lab",
    "notes": "Preferred slot 2 was occupied. Assigned next available conflict-free slot 3."
  },
  "route": {
    "algorithm_used": "A*",
    "path": ["Hostel", "Cafeteria", "Science_Block", "AI_Lab"],
    "cost": 6.0,
    "steps": 3
  },
  "message": "Your request has been accepted. You are assigned AI_Lab in slot 3. Follow the recommended route."
}
```

---

# 10. Error Handling & Rejection Protocol

The system MUST fail gracefully and provide explanatory diagnostics at four potential failure points:

### 10.1 Stage 1: Preprocessing Rejection
* **Triggers:** Missing required fields, illegal values (e.g., $severity > 10$, slot $\notin \{1,2,3,4\}$), unknown campus location.
* **Action:** Abort immediately. Return `decision = "rejected"` with validation error text.

### 10.2 Stage 2: Logic Gatekeeper Rejection
* **Triggers:** Student missing prerequisites (e.g., Sara), unregistered instructor, unauthorized lab request.
* **Action:** Terminate pipeline before CSP or Search are invoked. Return `decision = "rejected"` containing the rule deduction trace explaining why permission was denied.

### 10.3 Stage 3: CSP Overbooking Rejection
* **Triggers:** All slots full, unsolvable constraint deadlock.
* **Action:** Return `decision = "rejected"`, `notes = "No feasible conflict-free slot available under current constraints."`

### 10.4 Stage 4: Navigation Disconnection Rejection
* **Triggers:** Start or goal node unreachable.
* **Action:** Return `decision = "rejected"`, `message = "No viable path exists between selected landmarks."`

---

# 11. Academic Comparison & Benchmark Requirements

To satisfy course capstone evaluation rubrics, the system must support dual operating modes:

### 11.1 Operational Mode
Runs only the designated production algorithms: BFS for unweighted graphs, A* for weighted graphs, MLP for priority, and Backtracking with MRV/LCV/FC for CSP.

### 11.2 Benchmark / Comparison Mode
Executes and compares all 9 graph search algorithms from the lab curriculum on the same campus graph query:
1. Breadth-First Search (BFS)
2. Depth-First Search (DFS)
3. Depth-Limited Search (DLS)
4. Iterative Deepening Search (IDS)
5. Uniform-Cost Search (UCS)
6. Bidirectional BFS
7. Greedy Best-First Search
8. A* Search
9. Recursive Best-First Search (RBFS)

**Comparative Metrics Table Output:**
* Algorithm Name
* Path Cost
* Hop / Step Count
* Total Nodes Expanded
* Execution Time (milliseconds)

---

# 12. Evaluation Rubrics & Submission Criteria

### 12.1 Mark Allocation Rubric (100 Marks Total)

| Rubric Component | Allocated Marks | Assessment Focus |
| :--- | :---: | :--- |
| **Input & Preprocessing Module** | 10 | Structured CLI form, validation checks, normalization, 7-D feature vectorizer. |
| **ANN Priority Prediction Module** | 20 | Binary Perceptron baseline + Multiclass MLP ($7 \to 4 \to 3 \to 4$) forward pass. |
| **Logic / Knowledge Base Module** | 20 | Campus ontology, FOL rules, forward-chaining inference engine, gatekeeper trace. |
| **CSP Scheduler / Control Allocation** | 15 | 6-group viva CSP solver with MRV, Degree Heuristic, LCV, and Forward Checking. |
| **Search Navigation Module** | 15 | 13-node campus map, BFS (unweighted), A* (weighted), UCS, 9-algorithm benchmark. |
| **Final Response & Integration** | 10 | Request Router (5 canonical pipelines), Final Response Aggregator, Rejection Handler. |
| **Documentation & Code Quality** | 10 | Clean architecture, SOLID principles, function comment blocks, Word report & screenshots. |
| **Total** | **100** | |

### 12.2 Submission Deliverables
1. **Source Code Archive:** Submitted by one team member as a ZIP file named:  
   `24F-XXXX_24F-YYYY_24F-ZZZZ_Project.zip`
2. **Project Report (Microsoft Word / PDF):**
   * Overview of project architecture.
   * Theoretical description of all AI concepts used.
   * Code snippets of key algorithms.
   * Screenshots of all 5 request scenarios running in the CLI (including rejection cases and benchmark comparisons).
   * Module breakdown and sequence to run the program.
3. **Coding Standards:**
   * Every function must start with a descriptive docstring block describing its functionality, arguments, and return types.
   * Understandable variable names and proper indentation.
   * Comprehensive exception handling to avoid crashes on incorrect input.
