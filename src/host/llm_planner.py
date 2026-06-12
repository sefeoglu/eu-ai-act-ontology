<<<<<<< HEAD
"""Maps user goals to prototype pipeline actions."""

from typing import Dict


class LLMPlanner:
    """Deterministic planner for the prototype (LLM integration placeholder)."""
=======
"""Planner that maps user intents to prototype actions."""


class LLMPlanner:
    """Simple deterministic planner placeholder for the prototype."""
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7

    ACTIONS = {
        "list concepts": "extract_concepts",
        "validate ontology": "validate_ontology",
        "show mappings": "map_to_existing_ontologies",
<<<<<<< HEAD
        "show queries": "generate_sparql_queries",
        "export package": "export_github_package",
    }

    def create_plan(self, user_goal: str) -> Dict[str, str]:
        """Map a user goal to a named pipeline action."""
        action = self.ACTIONS.get(user_goal.strip().lower(), "extract_concepts")
        return {"goal": user_goal, "action": action, "status": "planned"}
=======
    }

    def create_plan(self, user_goal: str) -> dict:
        normalized = user_goal.strip().lower()
        action = self.ACTIONS.get(normalized, "extract_concepts")
        return {
            "goal": user_goal,
            "action": action,
            "status": "planned",
        }
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
