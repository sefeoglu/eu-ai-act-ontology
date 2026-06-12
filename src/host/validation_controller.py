"""Validation controller for prototype responses."""

from typing import Any


class ValidationController:
    """Performs lightweight output validation checks."""

    def validate_result(self, result: Any) -> dict:
        is_empty = result is None or result == [] or result == {}
        return {
            "is_valid": not is_empty,
            "result_type": type(result).__name__,
        }
