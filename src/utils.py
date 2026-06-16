"""Utility helpers for local file-path handling."""

from pathlib import Path
import json
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def data_path(*parts: str) -> Path:
    """Return an absolute path under the repository memory directory."""
    return PROJECT_ROOT / Path(*parts)


def ensure_file_exists(path: Path) -> Path:
    """Validate that a path exists and return it."""
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path

def parse_deep(value):
    """Recursively convert stringified JSON and JSON-line arrays into real objects."""
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


def json_formatted_mappings(src_text, json_text):

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