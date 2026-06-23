"""Utility helpers for local file-path handling."""

from pathlib import Path
import json
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def data_path(*parts: str) -> Path:
    """Return an absolute path under the repository memory directory."""

    """Args:
    *parts: str
        A variable number of string arguments representing subdirectories or file names under the memory directory.
    Returns:
    Path
        An absolute Path object pointing to the specified location under the memory directory.
    """
    return PROJECT_ROOT / Path(*parts)


def ensure_file_exists(path: Path) -> Path:
    """Validate that a path exists and return it."""
    """Args:
    path: Path
        The path to validate.
    Returns:
    Path
        The validated path if it exists.
    Raises:
    FileNotFoundError
        If the path does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path

def parse_nested_json_value(value):
    """Recursively convert stringified JSON and JSON-line arrays into real objects."""
    """Args:
    value: Any  
        The input value to parse, which can be a string, list, dict, or primitive type.
    Returns:
    Any
        The parsed value, where any stringified JSON structures have been converted into their corresponding Python objects (e.g., dicts, lists).
    """
    if isinstance(value, str):
        stripped_value = value.strip()
        try:
            return parse_nested_json_value(json.loads(stripped_value))
        except Exception:
            return value

    if isinstance(value, list):
        # JSON object split over many string lines
        if value and all(isinstance(item, str) for item in value):
            joined = "\n".join(value).strip()
            try:
                return parse_nested_json_value(json.loads(joined))
            except Exception:
                return [parse_nested_json_value(item) for item in value]
        return [parse_nested_json_value(item) for item in value]

    if isinstance(value, dict):
        return {
            key: parse_nested_json_value(nested_value)
            for key, nested_value in value.items()
        }

    return value


def collect_mapping_blocks(value):
    """Recursively collect all dict blocks that contain 'corresponding_classes' or 'corresponding_properties'."""
    
    """Args:
    value: Any
        The input value to search through, which can be a dict, list, or primitive type
    Returns:
        A list of dict blocks that contain 'corresponding_classes' or 'corresponding_properties'.
    """
    blocks = []
    if isinstance(value, dict):
        if "corresponding_classes" in value or "corresponding_properties" in value:
            blocks.append(value)
        for nested_value in value.values():
            blocks.extend(collect_mapping_blocks(nested_value))
    elif isinstance(value, list):
        for nested_value in value:
            blocks.extend(collect_mapping_blocks(nested_value))
    return blocks


def format_mapping_output_as_json(src_text):
    """Parse the raw output from the mapping LLM and extract cleanly formatted mappings."""

    """The LLM output may contain nested JSON, JSON-lines, or other stringified structures. This function recursively parses and extracts the relevant mapping information into a clean JSON format.
    Args:    src_text: str
        The raw string output from the mapping LLM, which may contain nested JSON structures or JSON-lines.
    Returns:
     str
        A JSON-formatted string containing the extracted mappings with a consistent structure.
    """

    parsed = parse_nested_json_value(json.loads(src_text))
    blocks = collect_mapping_blocks(parsed)

    classes = []
    properties = []

    for block in blocks:
        class_mappings = block.get("corresponding_classes", [])
        property_mappings = block.get("corresponding_properties", [])
        if isinstance(class_mappings, list):
            classes.extend(
                mapping_entry
                for mapping_entry in class_mappings
                if isinstance(mapping_entry, dict)
            )
        if isinstance(property_mappings, list):
            properties.extend(
                mapping_entry
                for mapping_entry in property_mappings
                if isinstance(mapping_entry, dict)
            )

    cleaned = {
        "corresponding_classes": classes,
        "corresponding_properties": properties
    }

    return json.dumps(cleaned, indent=2)