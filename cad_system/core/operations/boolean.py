"""Boolean operations for geometric parts."""

from ...part.base import Part
from ..geometry.base import Geometry, GeometryError

class BooleanOperationError(GeometryError):
    """Exception raised when a boolean operation fails."""
    pass

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
