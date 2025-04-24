"""Primitive geometry implementations."""

import pyvista as pv
from .base import Geometry, GeometryData, GeometryValidationError
from .types import GeometryType

class Box(Geometry):
    """Geometry implementation for a box primitive using PyVista."""
    
    def __init__(self, width: float = None, height: float = None, depth: float = None) -> None:
        """Initialize a box with given dimensions.
        
        Args:
            width: Box width (X dimension), optional for PyVista conversion
            height: Box height (Y dimension), optional for PyVista conversion
            depth: Box depth (Z dimension), optional for PyVista conversion
            
        Raises:
            ValueError: If any dimension is not positive when provided
        """
        super().__init__()
        
        if all(dim is not None for dim in (width, height, depth)):
            if any(dim <= 0 for dim in (width, height, depth)):
                raise ValueError("Box dimensions must be positive")
            
            self._data = GeometryData(
                type=GeometryType.BOX,
                parameters={
                    "width": width,
                    "height": height,
                    "depth": depth
                }
            )
    
    @classmethod
    def from_pyvista(cls, mesh: pv.PolyData) -> "Box":
        """Create a box from a PyVista mesh.
        
        Args:
            mesh: PyVista mesh to convert
            
        Returns:
            New Box instance
            
        Raises:
            GeometryValidationError: If mesh is invalid
        """
        if not cls._validate_mesh(mesh):
            raise GeometryValidationError("Invalid mesh provided")
            
        bounds = mesh.bounds
        width = bounds[1] - bounds[0]
        height = bounds[3] - bounds[2]
        depth = bounds[5] - bounds[4]
        
        instance = cls()
        instance._data = GeometryData(
            type=GeometryType.BOX,
            parameters={
                "width": width,
                "height": height,
                "depth": depth
            },
            mesh=mesh
        )
        return instance
    
    def _create_mesh(self) -> None:
        """Create PyVista mesh for box geometry."""
        width = self.data.parameters["width"]
        height = self.data.parameters["height"]
        depth = self.data.parameters["depth"]
        
        # Create box using PyVista's built-in box primitive centered at origin
        box = pv.Box(
            bounds=(-width/2, width/2,
                   -height/2, height/2,
                   -depth/2, depth/2)
        )
        # Ensure mesh is triangulated
        self._data.mesh = box.triangulate()
    
    @property
    def width(self) -> float:
        """Get box width."""
        return self.data.parameters["width"]
    
    @property
    def height(self) -> float:
        """Get box height."""
        return self.data.parameters["height"]
    
    @property
    def depth(self) -> float:
        """Get box depth."""
        return self.data.parameters["depth"]


class Cylinder(Geometry):
    """Geometry implementation for a cylinder primitive using PyVista."""
    
    def __init__(self, radius: float = None, height: float = None) -> None:
        """Initialize a cylinder with given dimensions.
        
        Args:
            radius: Cylinder radius, optional for PyVista conversion
            height: Cylinder height, optional for PyVista conversion
            
        Raises:
            ValueError: If radius or height is not positive when provided
        """
        super().__init__()
        
        if all(dim is not None for dim in (radius, height)):
            if radius <= 0 or height <= 0:
                raise ValueError("Cylinder radius and height must be positive")
            
            self._data = GeometryData(
                type=GeometryType.CYLINDER,
                parameters={
                    "radius": radius,
                    "height": height
                }
            )
            
    @classmethod
    def from_pyvista(cls, mesh: pv.PolyData) -> "Cylinder":
        """Create a cylinder from a PyVista mesh.
        
        Args:
            mesh: PyVista mesh to convert
            
        Returns:
            New Cylinder instance
            
        Raises:
            GeometryValidationError: If mesh is invalid
        """
        if not cls._validate_mesh(mesh):
            raise GeometryValidationError("Invalid mesh provided")
        
        bounds = mesh.bounds
        # Estimate radius as half the minimum of width/depth
        radius = min(bounds[1] - bounds[0], bounds[3] - bounds[2]) / 2
        height = bounds[5] - bounds[4]
        
        instance = cls()
        instance._data = GeometryData(
            type=GeometryType.CYLINDER,
            parameters={
                "radius": radius,
                "height": height
            },
            mesh=mesh
        )
        return instance
    
    def _create_mesh(self) -> None:
        """Create PyVista mesh for cylinder geometry."""
        radius = self.data.parameters["radius"]
        height = self.data.parameters["height"]
        
        # Create cylinder using PyVista's built-in cylinder primitive
        # Center at origin, aligned with Z axis
        cylinder = pv.Cylinder(
            radius=radius,
            height=height,
            center=(0, 0, 0),
            direction=(0, 0, 1),
            resolution=32  # Number of points in circular discretization
        )
        # Ensure mesh is triangulated
        self._data.mesh = cylinder.triangulate()
    
    @property
    def radius(self) -> float:
        """Get cylinder radius."""
        return self.data.parameters["radius"]
    
    @property
    def height(self) -> float:
        """Get cylinder height."""
        return self.data.parameters["height"]
