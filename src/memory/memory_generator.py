"""Generate procedural and declarative memory for the prototype agent."""

from src.memory.declarative_memory import DeclarativeMemory
from src.memory.procedural_memory import ProceduralMemory


class MemoryGenerator:
    """Build declarative/procedural memory objects from repository assets."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def generate_procedural_memory(self) -> dict:
        """Generate procedural memory metadata for the prototype."""
        procedural_memory = ProceduralMemory(self.config.get("procedural_pdf"))
        return procedural_memory.get_metadata()

    def split_text_into_chunks(self, text: str, chunk_size: int = 1_000) -> list[str]:
        """Split extracted text into fixed-size chunks (1000 chars by default) for LLM prompts."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        return [text[index:index + chunk_size] for index in range(0, len(text), chunk_size)]

    def split_pdf_into_chunks(self, text: str, chunk_size: int = 1_000) -> list[str]:
        """Backward-compatible alias that expects already extracted PDF text."""
        return self.split_text_into_chunks(text=text, chunk_size=chunk_size)

    def generate_declarative_memory(self) -> DeclarativeMemory:
        """Load declarative memory based on configuration or defaults."""
        memory = DeclarativeMemory()
        ontology_path = self.config.get("declarative_ontology")
        if ontology_path:
            memory.load(ontology_path)
        else:
            memory.load_default()
        return memory
