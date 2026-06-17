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

def parse_deep(value):
    """Recursively convert stringified JSON and JSON-line arrays into real objects."""
    """Args:
    value: Any  
        The input value to parse, which can be a string, list, dict, or primitive type.
    Returns:
    Any
        The parsed value, where any stringified JSON structures have been converted into their corresponding Python objects (e.g., dicts, lists).
    """
    if isinstance(value, str):
        s = value.strip()
        try:
            return parse_deep(json.loads(s))
        except Exception:
            return value

    if isinstance(value, list):
        # JSON object split over many string lines
        if value and all(isinstance(item, str) for item in value):
            joined = "\n".join(value).strip()
            try:
                return parse_deep(json.loads(joined))
            except Exception:
                return [parse_deep(item) for item in value]
        return [parse_deep(item) for item in value]

    if isinstance(value, dict):
        return {k: parse_deep(v) for k, v in value.items()}

    return value

def get_entity(mapping, side):
    """Support entity1/entity2 and source/target formats."""
    if side == "entity1":
        return mapping.get("entity1") or mapping.get("source")
    return mapping.get("entity2") or mapping.get("target")

def uri_or_label(entity):
    if isinstance(entity, dict):
        return entity.get("uri") or entity.get("label")
    return None


def collect_blocks(value):
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
        for v in value.values():
            blocks.extend(collect_blocks(v))
    elif isinstance(value, list):
        for v in value:
            blocks.extend(collect_blocks(v))
    return blocks


def json_formatted_mappings(src_text):
    """Parse the raw output from the mapping LLM and extract cleanly formatted mappings."""

    """The LLM output may contain nested JSON, JSON-lines, or other stringified structures. This function recursively parses and extracts the relevant mapping information into a clean JSON format.
    Args:    src_text: str
        The raw string output from the mapping LLM, which may contain nested JSON structures or JSON-lines.
    Returns:
     str
        A JSON-formatted string containing the extracted mappings with a consistent structure.
    """

    parsed = parse_deep(json.loads(src_text))
    blocks = collect_blocks(parsed)

    classes = []
    properties = []

    for block in blocks:
        c = block.get("corresponding_classes", [])
        p = block.get("corresponding_properties", [])
        if isinstance(c, list):
            classes.extend(x for x in c if isinstance(x, dict))
        if isinstance(p, list):
            properties.extend(x for x in p if isinstance(x, dict))

    cleaned = {
        "corresponding_classes": classes,
        "corresponding_properties": properties
    }

    return json.dumps(cleaned, indent=2)