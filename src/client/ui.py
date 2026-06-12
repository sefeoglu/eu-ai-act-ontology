"""CLI-facing UI helpers."""

from host.llm_planner import LLMPlanner
from host.mcp_client import MCPClient
from host.validation_controller import ValidationController


class PrototypeUI:
    """Orchestrates planner, execution, and validation."""

    def __init__(self) -> None:
        self.planner = LLMPlanner()
        self.client = MCPClient()
        self.validator = ValidationController()

    def run_goal(self, goal: str) -> dict:
        plan = self.planner.create_plan(goal)
        result = self.client.execute(plan["action"])
        validation = self.validator.validate_result(result)
        return {
            "plan": plan,
            "validation": validation,
            "result": result,
        }
