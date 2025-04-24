"""Base document implementation for managing parts and history."""

from typing import List, Optional, Any
from ..part.base import Part

class Document:
    """Represents a CAD document containing parts and history for undo/redo operations."""
    
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.parts: List[Part] = []
        self.history: List[Any] = []  # Could be a list of action objects
        self.redo_stack: List[Any] = []  # Stack for redo operations
    
    def add_part(self, part: Part) -> None:
        """Add a part to the document and record the operation in history.
        
        Args:
            part: The Part instance to add.
        """
        self.parts.append(part)
        self.history.append(('add', part))
    
    def get_part(self, name: str) -> Optional[Part]:
        """Retrieve a part by name.
        
        Args:
            name: The name of the part to retrieve.
        
        Returns:
            The Part instance if found, else None.
        """
        for p in self.parts:
            if p.name == name:
                return p
        return None
    
    def undo(self) -> Any:
        """Undo the last action in the document's history.
        
        Returns:
            The undone action.
        
        Raises:
            RuntimeError: If there are no actions to undo.
        """
        if not self.history:
            raise RuntimeError("No actions to undo.")
        return self.history.pop()
    
    def redo(self) -> None:
        """Redo the last undone action.
        
        Raises:
            RuntimeError: If there are no actions to redo.
        """
        if not self.redo_stack:
            raise RuntimeError("No actions to redo.")
        action = self.redo_stack.pop()
        if action[0] == 'add':
            part = action[1]
            self.parts.append(part)
        self.history.append(action)
