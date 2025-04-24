# System Patterns

This file documents recurring patterns and standards used in the project.
[2024-04-24 18:26:00] - Initial patterns documentation established.

## Coding Patterns

### Immutability Pattern
```python
def transform(self) -> "Same Type":
    # Create new instance instead of modifying
    new_geometry = self.geometry.clone()
    return Type(self.name, new_geometry, self.parameters.copy())
```

### Factory Methods Pattern
```python
@staticmethod
def create(params) -> "Type":
    # Create and return new instances
    return Type(name, geometry, parameters)
```

### Type Safety Pattern
```python
def method(self, param: Type) -> ReturnType:
    """Method description.
    
    Args:
        param: Parameter description.
    
    Returns:
        Return value description.
        
    Raises:
        ErrorType: Error description.
    """
```

## Architectural Patterns

### Document-Based Structure
* Documents contain Parts
* Parts contain Geometry
* History tracks operations
* Undo/Redo stack pattern

### Operation Flow
1. Validate inputs
2. Create new instances
3. Update history
4. Return results

### Error Handling
* Specific exception types
* Descriptive error messages
* Clear recovery paths
* Operation validation

## Testing Patterns

### Unit Test Structure
```python
def test_operation(self):
    # Arrange
    input = create_test_input()
    
    # Act
    result = perform_operation(input)
    
    # Assert
    self.assertEqual(expected, result)
```

### Test Categories
* Creation tests
* Transformation tests
* Boolean operation tests
* Error handling tests
* State management tests

## Documentation Patterns

### Code Documentation
* Clear docstrings
* Type hints
* Usage examples
* Error conditions

### API Documentation
* Method purpose
* Parameter details
* Return values
* Error cases
* Usage examples

## PyVista Integration Patterns
[2024-04-24 18:31:00] - Added PyVista integration patterns

### Geometry Conversion Pattern
```python
def to_pyvista(self) -> "pyvista.PolyData":
    """Convert internal geometry to PyVista format.
    
    Returns:
        PyVista mesh object representing the geometry.
    """
    # Convert internal representation to PyVista mesh
    return converted_mesh

def from_pyvista(cls, mesh: "pyvista.PolyData") -> "Geometry":
    """Create geometry from PyVista mesh.
    
    Args:
        mesh: PyVista mesh to convert.
        
    Returns:
        Internal geometry representation.
    """
    # Convert PyVista mesh to internal representation
    return converted_geometry
```

### Boolean Operation Pattern
```python
def boolean_operation(a: Part, b: Part, operation: str) -> Part:
    """Perform boolean operation using PyVista.
    
    Args:
        a: First part
        b: Second part
        operation: One of 'union', 'difference', 'intersection'
        
    Returns:
        New Part instance with operation result
        
    Raises:
        GeometryError: If operation fails
    """
    try:
        # Convert to PyVista
        mesh_a = a.geometry.to_pyvista()
        mesh_b = b.geometry.to_pyvista()
        
        # Perform operation
        if operation == 'union':
            result = mesh_a.boolean_union(mesh_b)
        elif operation == 'difference':
            result = mesh_a.boolean_difference(mesh_b)
        else:  # intersection
            result = mesh_a.boolean_intersection(mesh_b)
            
        # Convert back to internal geometry
        new_geometry = Geometry.from_pyvista(result)
        return Part(f"{operation}_result", new_geometry)
        
    except Exception as e:
        raise GeometryError(f"Boolean operation failed: {str(e)}")
```

### Error Handling Pattern
```python
def validate_mesh(mesh: "pyvista.PolyData") -> bool:
    """Validate PyVista mesh before operations.
    
    Args:
        mesh: PyVista mesh to validate.
        
    Returns:
        True if valid, raises exception if not.
        
    Raises:
        GeometryError: If mesh is invalid.
    """
    if not mesh.is_all_triangles():
        raise GeometryError("Mesh must be triangulated")
    if not mesh.is_manifold():
        raise GeometryError("Mesh must be manifold")
    return True
```

## Architectural Patterns [2025-04-24 21:53]
Package Organization Pattern:
- core/: System fundamentals, base classes, shared utilities
- part/: Part-specific logic and operations
- document/: Document handling and persistence

Module Interaction Pattern:
- Hierarchical dependency (document -> part -> core)
- Clear separation of concerns
- Explicit interface definitions between packages
