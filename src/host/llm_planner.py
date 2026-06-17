"""Maps user goals to prototype pipeline actions."""

from typing import Dict


PIPELINE_ACTIONS = {
    "memory_generation": "memory_generation",
    "generate_competency_questions": "generate_competency_questions",
    "extract_concepts": "extract_concepts",
    "map_to_existing_ontologies": "map_to_existing_ontologies",
    "generate_ontology": "generate_ontology",
    "generate_chapter_based_ontology": "generate_chapter_based_ontology",
    "borrow_concept_extraction": "borrow_concept_extraction",
}


class LLMPlanner:
    """Deterministic planner for the prototype (LLM integration placeholder)."""

    ACTIONS = PIPELINE_ACTIONS

    def create_plan(self, user_goal: str) -> Dict[str, str]:
        """Map a user goal to a named pipeline action."""
        """Args:
        user_goal: str
            A natural language description of the user's goal (e.g., "Generate an ontology that captures the concepts and relationships in the procedural document, and maps them to the declarative ontology.").
        Returns:
        Dict[str, str]
            A dictionary containing the original goal, the mapped action, and a status indicating that the plan has been created. The 'action' field corresponds to a key in the ACTIONS dictionary, which can be used by the MCPClient to execute the appropriate method on the OntologyGenerator.
        """
        action = self.ACTIONS[user_goal.strip().lower()]
        return {"goal": user_goal, "action": action, "status": "planned"}
