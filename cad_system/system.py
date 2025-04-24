"""Main CAD system interface."""

import json
from typing import Dict, Any, Optional
from .document.base import Document

class CADSystem:
    """The main CAD system interface for creating and managing documents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the CAD system.
        
        Args:
            config: Optional configuration dictionary.
        """
        self.config: Dict[str, Any] = config if config is not None else {}
        self.version: str = "1.0.0"
    
    def new_document(self, name: str) -> Document:
        """Create and return a new CAD document.
        
        Args:
            name: The name of the new document.
        
        Returns:
            A new Document instance.
        
        Raises:
            ValueError: If the document name is empty.
        """
        if not name:
            raise ValueError("Document name must not be empty.")
        return Document(name)
    
    def load_document(self, path: str) -> Document:
        """Load a document from disk by reading a JSON file.
        
        Args:
            path: The file path from which to load the document.
        
        Returns:
            The loaded Document instance.
        
        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        with open(path, "r") as f:
            data = json.load(f)
        doc = Document(data["name"])
        # TODO: Deserialize parts, history, and redo_stack if needed.
        return doc
