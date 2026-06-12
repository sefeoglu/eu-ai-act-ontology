"""Validates the output produced by a pipeline action."""

from typing import Any, Dict


class ValidationController:
    """Lightweight output validator for the prototype pipeline."""

    def validate_result(self, result: Any) -> Dict[str, Any]:
        """Check that *result* is non-empty and return a validation summary."""
        is_empty = result in (None, [], {}, "")
        return {
            "is_valid": not is_empty,
            "result_type": type(result).__name__,
        }
