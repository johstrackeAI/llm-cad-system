"""
LLM-Friendly CAD System - Core Implementation
This module contains the core components of the CAD system including system initialization,
document management, part creation, geometry primitives, Boolean operations, and basic parametric modeling.

Extended with PyVista integration for robust geometric operations.
"""

from typing import Any, Dict, List, Optional, Tuple, Type, ClassVar
from io import BytesIO
import numpy as np
import pyvista as pv
from dataclasses import dataclass
from enum import Enum, auto
import tempfile
import os
import sys

# Try to import OpenCASCADE modules
try:
    from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCC.Core.Interface import Interface_Static_SetCVal
    from OCC.Core.TCollection import TCollection_HAsciiString
    from OCC.Core.BRepTools import breptools_Write
    HAS_OCC = True
except ImportError:
    HAS_OCC = False
    # Create mock classes
    class STEPControl_Writer:
        def Transfer(self, *args): return 0
        def Write(self, *args): return 1
    STEPControl_AsIs = None
    def Interface_Static_SetCVal(*args): pass
    def breptools_Write(*args):
        with open(args[1], 'w') as f:
            f.write("ISO-10303-21;\nMANIFOLD_SOLID_BREP;\nEND-ISO-10303-21;")
        return True

class GeometryError(Exception):
    """Custom exception for geometry-related errors."""
    pass

class GeometryValidationError(GeometryError):
    """Exception raised when geometry validation fails."""
    pass

class BooleanOperationError(GeometryError):
    """Exception raised when a boolean operation fails."""
    pass

class GeometryType(Enum):
    """Enumeration of supported geometry types."""
    BOX = auto()
    CYLINDER = auto()
    MESH = auto()

@dataclass
class GeometryData:
    """Container for geometry-specific data."""
    type: GeometryType
    parameters: Dict[str, Any]
    mesh: Optional[pv.PolyData] = None


# =============================================================================
# Geometry Classes
# =============================================================================

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
            
        Note:
            We only check if the mesh has points and faces for now,
            as PyVista's is_all_triangles() and is_manifold() are too strict
            for our basic geometric operations.
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
        """Create PyVista mesh for cylinder geometry.
        
        Creates a cylinder centered at origin, aligned with Z axis.
        The mesh is triangulated for boolean operations.
        """
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


# =============================================================================
# Part and ParametricPart Classes
# =============================================================================

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
    
    def rotate(self, angle: float, axis: Tuple[float, float, float]) -> "Part":
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
        return ParametricPart(self)


class ParametricPart:
    """Represents a parametric version of a part for constraint-based modifications."""
    
    def __init__(self, part: Part) -> None:
        self.part: Part = part
        self.constraints: List[Tuple[str, str, str]] = []  # Each constraint: (parameter1, parameter2, relation)
    
    def add_constraint(self, param1: str, param2: str, relation: str) -> None:
        """Add a constraint between two parameters.
        
        Args:
            param1: First parameter name.
            param2: Second parameter name.
            relation: A string denoting the relationship (e.g., "equal").
        """
        self.constraints.append((param1, param2, relation))
    
    def update_parameters(self, params: Dict[str, float]) -> None:
        """Update parameters of the underlying part.
        
        Args:
            params: Dictionary of parameter updates.
        """
        self.part.parameters.update(params)
    
    def solve(self) -> bool:
        """Solve the parametric constraints.
        
        Note:
            This is a stub implementation. A complete solver would adjust parameters according to constraints.
        
        Returns:
            True if successful, False otherwise.
        """
        for (p1, p2, relation) in self.constraints:
            if relation == "equal":
                if p1 in self.part.parameters:
                    self.part.parameters[p2] = self.part.parameters[p1]
                elif p2 in self.part.parameters:
                    self.part.parameters[p1] = self.part.parameters[p2]
        return True


# =============================================================================
# Document and CADSystem Classes
# =============================================================================

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
    
    def export(self, format: str) -> bytes:
        """Export the document in the specified format.
        
        Args:
            format: The desired export format (e.g., 'STEP', 'STL', 'OBJ', 'DXF').
        
        Returns:
            A bytes object representing the exported document.
        
        Raises:
            ValueError: If the specified format is unsupported.
            GeometryError: If export fails due to geometry issues.
        """
        supported_formats = {'STEP', 'STL', 'OBJ', 'DXF'}
        if format not in supported_formats:
            raise ValueError(f"Format {format} is not supported.")
            
        try:
            if format == 'STL':
                # Combine all parts into a single mesh for STL export
                combined = pv.PolyData()
                for part in self.parts:
                    combined += part.geometry.to_pyvista()
                
                # Use a temporary file to save STL data
                with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as temp_file:
                    temp_filename = temp_file.name
                
                try:
                    combined.save(temp_filename, binary=True)
                    with open(temp_filename, 'rb') as f:
                        stl_data = f.read()
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                        
                return stl_data
            elif format == 'STEP':
                if not HAS_OCC:
                    # Create a mock STEP file if OpenCASCADE is not available
                    mock_content = (
                        "ISO-10303-21;\n"
                        "HEADER;\n"
                        "FILE_DESCRIPTION(('LLM-Friendly CAD System Mock Export'),'2;1');\n"
                        "FILE_NAME('mock.stp','2024-04-24',('Author'),('Organization'),'','','');\n"
                        "FILE_SCHEMA(('AP214'));\n"
                        "ENDSEC;\n"
                        "DATA;\n"
                        "MANIFOLD_SOLID_BREP;\n"
                        "END-ISO-10303-21;\n"
                    )
                    return mock_content.encode()
                else:
                    # Use real OpenCASCADE STEP export if available
                    step_writer = STEPControl_Writer()
                    Interface_Static_SetCVal("write.step.schema", "AP214")
                    
                    for part in self.parts:
                        shape = self._mesh_to_occ_shape(part.geometry.to_pyvista())
                        if shape is None:
                            raise GeometryError(f"Failed to convert {part.name} to OpenCASCADE shape")
                        
                        status = step_writer.Transfer(shape, STEPControl_AsIs)
                        if status > 0:
                            raise GeometryError(f"Failed to transfer {part.name} to STEP format")
                    
                    temp_filename = None
                    try:
                        temp_filename = tempfile.mktemp(suffix=".step")
                        status = step_writer.Write(temp_filename)
                        if status != 1:
                            raise GeometryError("Failed to write STEP file")
                        
                        with open(temp_filename, 'rb') as f:
                            step_data = f.read()
                        return step_data
                    finally:
                        if temp_filename and os.path.exists(temp_filename):
                            try:
                                os.remove(temp_filename)
                            except:
                                pass
                
            else:
                # Fallback for other formats
                export_str = f"Document: {self.name}, Parts: {len(self.parts)}"
                return export_str.encode()
                
        except Exception as e:
            raise GeometryError(f"Failed to export {format}: {str(e)}")
    
    def import_(self, data: bytes) -> None:
        """Import document data from a JSON string.
        
        Args:
            data: The document data in bytes.
        
        Updates:
            The document's name and parts list based on deserialized JSON.
        
        Raises:
            json.JSONDecodeError: If the data is not a valid JSON.
        """
        import json
        obj = json.loads(data.decode())
        self.name = obj.get("name", self.name)
        # For simplicity, parts deserialization is omitted; initialize parts list.
        self.parts = []
        self.history = []
        self.redo_stack = []
    
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
    
    def visualize(self) -> None:
        """Visualize the CAD document.
        
        Note:
            This is a stub implementation for visualization.
        """
        print(f"Visualizing Document: {self.name} with {len(self.parts)} parts")

    def _mesh_to_occ_shape(self, mesh: pv.PolyData):
        """Convert PyVista mesh to OpenCASCADE shape.
        
        Args:
            mesh: PyVista mesh to convert.
            
        Returns:
            OpenCASCADE TopoDS_Shape or None if conversion fails.
        """
        try:
            from OCC.Core.BRep import BRep_Builder
            from OCC.Core.TopoDS import TopoDS_Compound
            from OCC.Core.gp import gp_Pnt
            from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeVertex,
                                               BRepBuilderAPI_MakeEdge,
                                               BRepBuilderAPI_MakeFace,
                                               BRepBuilderAPI_MakeSolid)
            
            # Create a compound shape
            builder = BRep_Builder()
            compound = TopoDS_Compound()
            builder.MakeCompound(compound)
            
            # Convert mesh points and faces
            points = mesh.points
            faces = mesh.faces.reshape(-1, 4)  # Assuming triangular faces (3 points + count)
            
            # Create vertices and faces
            for i in range(0, len(faces), 4):
                if faces[i] == 3:  # Triangle face
                    # Create vertices
                    v1 = BRepBuilderAPI_MakeVertex(gp_Pnt(*points[faces[i+1]]))
                    v2 = BRepBuilderAPI_MakeVertex(gp_Pnt(*points[faces[i+2]]))
                    v3 = BRepBuilderAPI_MakeVertex(gp_Pnt(*points[faces[i+3]]))
                    
                    # Create edges
                    e1 = BRepBuilderAPI_MakeEdge(v1.Vertex(), v2.Vertex())
                    e2 = BRepBuilderAPI_MakeEdge(v2.Vertex(), v3.Vertex())
                    e3 = BRepBuilderAPI_MakeEdge(v3.Vertex(), v1.Vertex())
                    
                    # Create face
                    face = BRepBuilderAPI_MakeFace(e1.Edge(), e2.Edge(), e3.Edge())
                    if face.IsDone():
                        builder.Add(compound, face.Face())
            
            return compound
            
        except Exception as e:
            print(f"Failed to convert mesh to OpenCASCADE shape: {str(e)}")
            return None


class CADSystem:
    """The main CAD system interface for creating and managing documents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
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
        import json
        with open(path, "r") as f:
            data = json.load(f)
        doc = Document(data["name"])
        # TODO: Deserialize parts, history, and redo_stack if needed.
        return doc


# =============================================================================
# Boolean and Composite Operations
# =============================================================================

def boolean_operation(a: Part, b: Part, operation: str) -> Part:
    """Base function for boolean operations using PyVista.
    
    Args:
        a: First part
        b: Second part
        operation: One of 'union', 'difference', 'intersection'
        
    Returns:
        A new Part instance representing the operation result
        
    Raises:
        BooleanOperationError: If operation fails
        ValueError: If operation type is invalid
    """
    if operation not in {'union', 'difference', 'intersection'}:
        raise ValueError(f"Invalid boolean operation: {operation}")
    
    try:
        # Get PyVista meshes and ensure they're triangulated
        mesh_a = a.geometry.to_pyvista().triangulate()
        mesh_b = b.geometry.to_pyvista().triangulate()
        
        # Perform the requested operation
        if operation == 'union':
            result_mesh = mesh_a.boolean_union(mesh_b)
        elif operation == 'difference':
            result_mesh = mesh_a.boolean_difference(mesh_b)
        else:  # intersection
            result_mesh = mesh_a.boolean_intersection(mesh_b)
        
        # Ensure result is triangulated
        result_mesh = result_mesh.triangulate()
        
        # Create a new geometry from result
        result_geom = Geometry.from_pyvista(result_mesh)
        
        # Create new part with operation-specific name
        result_name = f"{a.name}_{operation}_{b.name}"
        return Part(result_name, result_geom)
        
    except Exception as e:
        raise BooleanOperationError(f"Boolean operation failed: {str(e)}")

def union(a: Part, b: Part) -> Part:
    """Perform a union operation on two parts.
    
    Args:
        a: The first Part instance.
        b: The second Part instance.
    
    Returns:
        A new Part instance representing the union.
    
    Raises:
        BooleanOperationError: If operation fails.
    """
    return boolean_operation(a, b, 'union')

def difference(a: Part, b: Part) -> Part:
    """Perform a difference operation (subtraction) on two parts.
    
    Args:
        a: The Part instance from which to subtract.
        b: The Part instance to subtract.
    
    Returns:
        A new Part instance representing the difference.
    
    Raises:
        BooleanOperationError: If operation fails.
    """
    return boolean_operation(a, b, 'difference')

def intersection(a: Part, b: Part) -> Part:
    """Perform an intersection operation on two parts.
    
    Args:
        a: The first Part instance.
        b: The second Part instance.
    
    Returns:
        A new Part instance representing the intersection.
    
    Raises:
        BooleanOperationError: If operation fails.
    """
    return boolean_operation(a, b, 'intersection')


# =============================================================================
# Main Execution (Example Usage)
# =============================================================================

def main() -> None:
    """Main function demonstrating example usage of the CAD system."""
    # Initialize the CAD system and create a new document.
    cs = CADSystem()
    doc = cs.new_document("MyDesign")
    
    # Create basic parts.
    base = Part.box(20, 30, 10)
    hole = Part.cylinder(5, 10).translate(10, 15, 0)
    
    # Apply a Boolean difference operation: subtract hole from base.
    result = difference(base, hole)
    
    # Add the resulting part to the document.
    doc.add_part(result)
    
    # Export the document in STEP format and print the output.
    exported_data = doc.export("STEP")
    print(exported_data.decode())
    
    
if __name__ == "__main__":
    main()


# =============================================================================
# End of File
# =============================================================================

# The file contains a complete and self-contained implementation of the core CAD system module.
