"""Maps user goals to prototype pipeline actions."""

from typing import Dict


class LLMPlanner:
    """Deterministic planner for the prototype (LLM integration placeholder)."""

    ACTIONS = {
        "memory_generation": "memory_generation",
        "generate_competency_questions": "generate_competency_questions",
        "extract_concepts": "extract_concepts",
        "validate_ontology": "validate_ontology",
        "map_to_existing_ontologies": "map_to_existing_ontologies",
        "generate_ontology": "generate_ontology",
        "borrow_concept_extraction": "borrow_concept_extraction"
    }

    def create_plan(self, user_goal: str) -> Dict[str, str]:
        """Map a user goal to a named pipeline action."""
        action = self.ACTIONS[user_goal.strip().lower()]
        return {"goal": user_goal, "action": action, "status": "planned"}
