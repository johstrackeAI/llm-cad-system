"""Base implementation of CAD parts."""

from typing import Dict, Any, Optional
from ..core.geometry.base import Geometry
from ..core.geometry.primitives import Box, Cylinder

class Part:
    """Represents a single CAD part and its associated geometry."""
    
    def __init__(self, name: str, geometry: Geometry, parameters: Optional[Dict[str, Any]] = None) -> None:
        self.name: str = name
        self.geometry: Geometry = geometry
        self.parameters: Dict[str, Any] = parameters if parameters is not None else {}
    
    @staticmethod
    def box(width: float, height: float, depth: float) -> "Part":
        """Factory method to create a box primitive.
        
        Args:
            width: Width of the box.
            height: Height of the box.
            depth: Depth of the box.
        
        Returns:
            A Part instance representing the box.
        """
        geometry = Box(width, height, depth)
        return Part("Box", geometry, {"width": width, "height": height, "depth": depth})
    
    @staticmethod
    def cylinder(radius: float, height: float) -> "Part":
        """Factory method to create a cylinder primitive.
        
        Args:
            radius: Radius of the cylinder.
            height: Height of the cylinder.
        
        Returns:
            A Part instance representing the cylinder.
        """
        geometry = Cylinder(radius, height)
        return Part("Cylinder", geometry, {"radius": radius, "height": height})
    
    def translate(self, x: float, y: float, z: float) -> "Part":
        """Translate the part, returning a new Part instance.
        
        Args:
            x: Translation along the X-axis.
            y: Translation along the Y-axis.
            z: Translation along the Z-axis.
        
        Returns:
            A new translated Part instance.
        """
        new_geometry = self.geometry.translate(x, y, z)
        return Part(self.name, new_geometry, self.parameters.copy())
    
    def rotate(self, angle: float, axis: tuple[float, float, float]) -> "Part":
        """Rotate the part, returning a new Part instance.
        
        Args:
            angle: Rotation angle in degrees.
            axis: Rotation axis as (x, y, z).
        
        Returns:
            A new rotated Part instance.
        """
        new_geometry = self.geometry.rotate(angle, axis)
        return Part(self.name, new_geometry, self.parameters.copy())
    
    def clone(self) -> "Part":
        """Return a deep copy of the part.
        
        Returns:
            A new cloned Part instance.
        """
        return Part(self.name, self.geometry.clone(), self.parameters.copy())
    
    def parameterize(self) -> "ParametricPart":
        """Convert this part into a parametric model.
        
        Returns:
            A ParametricPart instance for parameter-based modifications.
        """
        from .parametric import ParametricPart  # Import here to avoid circular dependency
        return ParametricPart(self)
