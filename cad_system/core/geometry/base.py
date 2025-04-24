"""Base geometry classes and data structures."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, Tuple
import pyvista as pv
from .types import GeometryType

class GeometryError(Exception):
    """Custom exception for geometry-related errors."""
    pass

class GeometryValidationError(GeometryError):
    """Exception raised when geometry validation fails."""
    pass

@dataclass
class GeometryData:
    """Container for geometry-specific data."""
    type: GeometryType
    parameters: Dict[str, Any]
    mesh: Optional[pv.PolyData] = None

class Geometry:
    """Abstract Geometry base class defining core API for all geometric primitives."""
    
    def __init__(self) -> None:
        self._data: GeometryData = None
        
    @property
    def data(self) -> GeometryData:
        """Get the geometry data."""
        if self._data is None:
            raise GeometryError("Geometry data not initialized")
        return self._data
    
    def to_pyvista(self) -> pv.PolyData:
        """Convert geometry to PyVista mesh.
        
        Returns:
            PyVista PolyData mesh representing the geometry.
            
        Raises:
            GeometryError: If conversion fails.
        """
        if self.data.mesh is None:
            self._create_mesh()
        return self.data.mesh
    
    @classmethod
    def from_pyvista(cls: Type["Geometry"], mesh: pv.PolyData) -> "Geometry":
        """Create geometry from PyVista mesh.
        
        Args:
            mesh: PyVista mesh to convert.
            
        Returns:
            New Geometry instance.
            
        Raises:
            GeometryValidationError: If mesh is invalid.
        """
        if not cls._validate_mesh(mesh):
            raise GeometryValidationError("Invalid mesh provided")
        instance = cls()
        instance._data = GeometryData(
            type=GeometryType.MESH,
            parameters={},
            mesh=mesh
        )
        return instance
    
    @staticmethod
    def _validate_mesh(mesh: pv.PolyData) -> bool:
        """Validate a PyVista mesh.
        
        Args:
            mesh: PyVista mesh to validate.
            
        Returns:
            True if valid, False if not.
        """
        try:
            return (mesh.n_points > 0 and
                   mesh.n_cells > 0 and
                   isinstance(mesh, pv.PolyData))
        except Exception as e:
            return False
    
    def _create_mesh(self) -> None:
        """Create PyVista mesh from internal parameters.
        
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("_create_mesh() must be implemented by subclasses.")
    
    def bounding_box(self) -> Tuple[float, float, float]:
        """Compute the bounding box of the geometry using PyVista.
        
        Returns:
            Tuple containing (width, height, depth).
        """
        mesh = self.to_pyvista()
        bounds = mesh.bounds
        return (
            bounds[1] - bounds[0],  # width
            bounds[3] - bounds[2],  # height
            bounds[5] - bounds[4]   # depth
        )
    
    def translate(self, x: float, y: float, z: float) -> "Geometry":
        """Translate the geometry along (x, y, z) axes.
        
        Args:
            x: Translation along the X-axis.
            y: Translation along the Y-axis.
            z: Translation along the Z-axis.
        
        Returns:
            A new Geometry instance translated.
        """
        mesh = self.to_pyvista()
        translated = mesh.translate((x, y, z))
        return self.from_pyvista(translated)
    
    def rotate(self, angle: float, axis: Tuple[float, float, float]) -> "Geometry":
        """Rotate the geometry.
        
        Args:
            angle: Rotation angle in degrees.
            axis: Rotation axis as a tuple (x, y, z).
        
        Returns:
            A new Geometry instance rotated.
        """
        mesh = self.to_pyvista()
        rotated = mesh.rotate_vector(axis, angle)
        return self.from_pyvista(rotated)
    
    def clone(self) -> "Geometry":
        """Create a clone of the geometry.
        
        Returns:
            A new cloned instance of the Geometry.
        """
        mesh = self.to_pyvista()
        return self.from_pyvista(mesh.copy(deep=True))
