"""Generate procedural and declarative memory for the agent."""


from os import read

from memory import memory


class MemoryGenerator(object):
    """Generate procedural and declarative memory for the agent."""

    def __init__(self, config):
        self.config = config

    def generate_procedural_memory(self):
        """Generate procedural memory for the agent."""
        """Apply Gemini to read text in pdf and generate procedural memory for the agent."""
        pass    
    def split_pdf_into_chunks(self, pdf_path):
        """Split a PDF file into chunks for processing."""
        # Code to split the PDF into manageable chunks
        pass

    def generate_declarative_memory(self):
        """Generate declarative memory for the agent."""
        # Code to generate declarative memory based on the configuration
        pass