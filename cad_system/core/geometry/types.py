"""Geometry types and custom exceptions."""

from enum import Enum, auto

class GeometryType(Enum):
    """Enumeration of supported geometry types."""
    BOX = auto()
    CYLINDER = auto()
    MESH = auto()

class GeometryError(Exception):
    """Base class for geometry-related errors."""
    pass

class GeometryValidationError(GeometryError):
    """Error raised when geometry validation fails."""
    pass

class BooleanOperationError(GeometryError):
    """Error raised when a boolean operation fails."""
    pass
