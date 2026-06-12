"""Maps user goals to prototype pipeline actions."""

from typing import Dict


class LLMPlanner:
    """Deterministic planner for the prototype (LLM integration placeholder)."""

    ACTIONS = {
        "pdf to text": "ocr_pdf",
        "generate competency questions": "generate_competency_questions",
        "list concepts": "extract_concepts",
        "validate ontology": "validate_ontology",
        "show mappings": "map_to_existing_ontologies",
        "show queries": "generate_sparql_queries",
        "export package": "export_github_package",
    }

    def create_plan(self, user_goal: str) -> Dict[str, str]:
        """Map a user goal to a named pipeline action."""
        action = self.ACTIONS.get(user_goal.strip().lower(), "extract_concepts")
        return {"goal": user_goal, "action": action, "status": "planned"}
