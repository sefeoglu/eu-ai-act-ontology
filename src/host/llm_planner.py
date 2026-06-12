"""Planner that maps user intents to prototype actions."""


class LLMPlanner:
    """Simple deterministic planner placeholder for the prototype."""

    ACTIONS = {
        "list concepts": "extract_concepts",
        "validate ontology": "validate_ontology",
        "show mappings": "map_to_existing_ontologies",
    }

    def create_plan(self, user_goal: str) -> dict:
        normalized = user_goal.strip().lower()
        action = self.ACTIONS.get(normalized, "extract_concepts")
        return {
            "goal": user_goal,
            "action": action,
            "status": "planned",
        }
