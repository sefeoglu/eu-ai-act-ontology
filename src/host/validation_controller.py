<<<<<<< HEAD
"""Validates the output produced by a pipeline action."""

from typing import Any, Dict


class ValidationController:
    """Lightweight output validator for the prototype pipeline."""

    def validate_result(self, result: Any) -> Dict[str, Any]:
        """Check that *result* is non-empty and return a validation summary."""
        is_empty = result in (None, [], {}, "")
=======
"""Validation controller for prototype responses."""

from typing import Any


class ValidationController:
    """Performs lightweight output validation checks."""

    def validate_result(self, result: Any) -> dict:
        is_empty = result is None or result == [] or result == {}
>>>>>>> c919a5e89154ffc1874e609501d11bf3d767f3c7
        return {
            "is_valid": not is_empty,
            "result_type": type(result).__name__,
        }
