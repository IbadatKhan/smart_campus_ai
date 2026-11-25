"""
First-Order Logic Knowledge Base & Security Gatekeeper Module
Implements first-order predicates, Horn clause rules, Generalized Modus Ponens
forward chaining, and prerequisite verification gatekeeper logic.
"""

from typing import Dict, List, Optional, Set, Tuple
from core.contracts import ILogicVerifier
from core.models import LogicResult


class FOLPredicate:
    """
    First-Order Logic atom: PredicateName(arg1, arg2, ...).
    Variables are lowercase identifiers (e.g., 'x', 'c');
    constants are capitalized strings (e.g., 'Ali', 'AI').
    """

    def __init__(self, name: str, *args: str) -> None:
        self.name = name
        self.args = tuple(args)

    def is_ground(self) -> bool:
        """Returns True if atom contains no unbound variables."""
        return all(arg[0].isupper() for arg in self.args if arg)

    def substitute(self, bindings: Dict[str, str]) -> "FOLPredicate":
        """Replaces variables with bound constant values."""
        new_args = [bindings.get(arg, arg) for arg in self.args]
        return FOLPredicate(self.name, *new_args)

    def match(self, ground_fact: "FOLPredicate") -> Optional[Dict[str, str]]:
        """
        Unifies atom against a ground fact.
        Returns variable bindings dict on match, or None on mismatch.
        """
        if self.name != ground_fact.name or len(self.args) != len(ground_fact.args):
            return None

        bindings: Dict[str, str] = {}
        for pattern_arg, fact_arg in zip(self.args, ground_fact.args):
            if pattern_arg[0].islower():
                # Variable argument: check consistency if already bound
                if pattern_arg in bindings and bindings[pattern_arg] != fact_arg:
                    return None
                bindings[pattern_arg] = fact_arg
            else:
                # Constant argument must match verbatim
                if pattern_arg != fact_arg:
                    return None
        return bindings

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FOLPredicate):
            return False
        return self.name == other.name and self.args == other.args

    def __hash__(self) -> int:
        return hash((self.name, self.args))

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(self.args)})"


class FOLRule:
    """
    Implication rule: Antecedents => Consequent.
    Example: Student(x) ^ Completed(x, ProgrammingFundamentals) => Eligible(x, AI)
    """

    def __init__(
        self,
        name: str,
        antecedents: List[FOLPredicate],
        consequent: FOLPredicate
    ) -> None:
        self.name = name
        self.antecedents = antecedents
        self.consequent = consequent

    def __repr__(self) -> str:
        premises = " ^ ".join(str(p) for p in self.antecedents)
        return f"[{self.name}] {premises} => {self.consequent}"


class FOLKnowledgeBase:
    """
    Working memory fact base with Generalized Modus Ponens forward-chaining.
    Deduces new facts iteratively until fixed point or goal query is reached.
    """

    def __init__(self) -> None:
        self.facts: Set[FOLPredicate] = set()
        self.rules: List[FOLRule] = []
        self.load_default_campus_kb()

    def tell_fact(self, fact: FOLPredicate) -> None:
        """Adds a verified ground fact to working memory."""
        self.facts.add(fact)

    def tell_rule(self, rule: FOLRule) -> None:
        """Registers a logical implication rule."""
        self.rules.append(rule)

    def load_default_campus_kb(self) -> None:
        """Populates default campus facts and rules defined in specifications."""
        # Initial ground facts
        self.tell_fact(FOLPredicate("Student", "Ali"))
        self.tell_fact(FOLPredicate("Student", "Sara"))
        self.tell_fact(FOLPredicate("Completed", "Ali", "ProgrammingFundamentals"))
        self.tell_fact(FOLPredicate("Teaches", "DrKhan", "AI"))
        self.tell_fact(FOLPredicate("Enrolled", "Ali", "AI"))

        # Rule R1: Prerequisite satisfaction for AI Lab
        self.tell_rule(FOLRule(
            "R1",
            [
                FOLPredicate("Student", "x"),
                FOLPredicate("Completed", "x", "ProgrammingFundamentals")
            ],
            FOLPredicate("Eligible", "x", "AI")
        ))

        # Rule R2: Instructor course authorization
        self.tell_rule(FOLRule(
            "R2",
            [FOLPredicate("Teaches", "x", "AI")],
            FOLPredicate("Instructor", "x", "AI")
        ))

        # Rule R3: Student lab facility access
        self.tell_rule(FOLRule(
            "R3",
            [FOLPredicate("Enrolled", "x", "AI")],
            FOLPredicate("UsesLab", "x", "Lab1")
        ))

        # Rule R4: Faculty lab facility access
        self.tell_rule(FOLRule(
            "R4",
            [FOLPredicate("Instructor", "x", "AI")],
            FOLPredicate("UsesLab", "x", "Lab1")
        ))

    def forward_chain(self, query: FOLPredicate) -> Tuple[bool, List[str]]:
        """
        Executes forward chaining via Modus Ponens to determine if query atom is entailed.
        Returns (is_entailed, derivation_trace).
        """
        derivation_trace: List[str] = []

        if query in self.facts:
            derivation_trace.append(f"Query {query} already known as given fact.")
            return True, derivation_trace

        known_facts = set(self.facts)
        new_fact_derived = True

        while new_fact_derived:
            new_fact_derived = False

            for rule in self.rules:
                # Find all valid variable substitutions that satisfy rule antecedents
                matching_bindings = self._find_satisfying_bindings(rule.antecedents, known_facts)

                for binding in matching_bindings:
                    inferred_fact = rule.consequent.substitute(binding)

                    if inferred_fact not in known_facts:
                        known_facts.add(inferred_fact)
                        new_fact_derived = True
                        step_note = (
                            f"Applied [{rule.name}] with bindings {binding} "
                            f"-> Inferred: {inferred_fact}"
                        )
                        derivation_trace.append(step_note)

                        if inferred_fact == query:
                            # Update working memory with derived fact
                            self.facts.add(inferred_fact)
                            return True, derivation_trace

        # Goal was not entailed
        entailed = query in known_facts
        return entailed, derivation_trace

    def _find_satisfying_bindings(
        self, antecedents: List[FOLPredicate], facts: Set[FOLPredicate]
    ) -> List[Dict[str, str]]:
        """
        Recursively matches a list of antecedent patterns against known facts.
        """
        def _match_conjunction(
            patterns: List[FOLPredicate], current_bindings: Dict[str, str]
        ) -> List[Dict[str, str]]:
            if not patterns:
                return [dict(current_bindings)]

            pattern = patterns[0].substitute(current_bindings)
            results: List[Dict[str, str]] = []

            for fact in facts:
                match_result = pattern.match(fact)
                if match_result is not None:
                    # Merge existing bindings with newly unified variables
                    merged = dict(current_bindings)
                    merged.update(match_result)
                    sub_results = _match_conjunction(patterns[1:], merged)
                    results.extend(sub_results)

            return results

        return _match_conjunction(antecedents, {})


class LogicKBGatekeeper(ILogicVerifier):
    """
    Security gatekeeper service implementing ILogicVerifier port.
    Enforces university policy verification and fail-fast circuit breaker.
    """

    def __init__(self, kb: Optional[FOLKnowledgeBase] = None) -> None:
        self.kb = kb or FOLKnowledgeBase()

    def verify_request_eligibility(
        self, user_name: str, role: str, category: str
    ) -> LogicResult:
        """
        Verifies if user satisfies course prerequisites and role permissions.
        Acts as circuit breaker: returns allowed=False on unauthorized access.
        """
        normalized_role = (role or "").strip().lower()
        normalized_cat = (category or "").strip()

        # Gate 1: AI Lab Support prerequisite check
        if normalized_cat in ["AI_Lab_Support", "AI_Lab"]:
            query = FOLPredicate("Eligible", user_name, "AI")
            entailed, trace = self.kb.forward_chain(query)

            if entailed:
                return LogicResult(
                    allowed=True,
                    explanation=f"Access granted: {user_name} verified for AI Lab prerequisites.",
                    deduction_trace=trace
                )
            else:
                return LogicResult(
                    allowed=False,
                    explanation=(
                        f"Access denied: {user_name} has not completed prerequisite "
                        f"'ProgrammingFundamentals' required for AI Lab services."
                    ),
                    deduction_trace=trace or [f"Could not prove {query} from campus knowledge base."]
                )

        # Gate 2: Viva examination scheduling requires academic faculty/staff role
        if normalized_cat in ["Viva_Scheduling", "Viva_Schedule"]:
            if normalized_role in ["instructor", "staff"]:
                return LogicResult(
                    allowed=True,
                    explanation=f"Authorized: {user_name} ({normalized_role}) permitted to schedule vivas."
                )
            return LogicResult(
                allowed=False,
                explanation=f"Access denied: Role '{normalized_role}' is not authorized to create examination schedules."
            )

        # Gate 3: Administrative Access Request
        if normalized_cat == "Access_Request":
            if normalized_role in ["staff", "instructor"]:
                return LogicResult(
                    allowed=True,
                    explanation=f"Authorized: Facility access granted for role '{normalized_role}'."
                )
            return LogicResult(
                allowed=False,
                explanation="Access denied: Student access request requires prior administrative clearance."
            )

        # Default: Maintenance & Emergency help accessible to all registered roles
        return LogicResult(
            allowed=True,
            explanation=f"Request permitted under operational category '{normalized_cat}'."
        )

    def query_fact(self, fol_query_string: str) -> LogicResult:
        """
        Evaluates arbitrary FOL query string via forward chaining.
        Example string: 'Eligible(Ali, AI)'
        """
        try:
            name, rest = fol_query_string.split("(", 1)
            name = name.strip()
            args = [a.strip() for a in rest.rstrip(")").split(",") if a.strip()]
            query = FOLPredicate(name, *args)
            entailed, trace = self.kb.forward_chain(query)
            return LogicResult(
                allowed=entailed,
                explanation=f"Query {query} entailed: {entailed}",
                deduction_trace=trace
            )
        except Exception as e:
            return LogicResult(
                allowed=False,
                explanation=f"Query parse error: {str(e)}"
            )
