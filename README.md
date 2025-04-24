# LLM-Friendly CAD System

A Computer-Aided Design (CAD) system specifically designed for easy programmability and use by LLM-powered agents. The system provides both 2D and 3D capabilities through a Python API with an object-oriented design.

## Features

- Easy to use programmatically
- Clear and predictable behavior
- Comprehensive error messages
- Well-documented interfaces
- Support for both immediate and parametric modeling
- Scalable for complex designs

## Core Components

- Geometry primitives (Box, Cylinder)
- Part creation and transformations
- Boolean operations (union, difference, intersection)
- Parametric modeling support
- Document management with undo/redo capability

## Usage Example

```python
from cad_system import CADSystem, Part

# Initialize the system
cs = CADSystem()
doc = cs.new_document("MyDesign")

# Create parts
base = Part.box(20, 30, 10)
hole = Part.cylinder(5, 10).translate(10, 15, 0)

# Perform Boolean operation
result = difference(base, hole)

# Add to document
doc.add_part(result)

# Export
exported_data = doc.export("STEP")
```

## Development Status

This is an initial implementation with some features still in development:

- Boolean operations are currently stubs
- Visualization backend to be implemented
- Advanced constraint solving for parametric design in progress
- File I/O support for various formats planned

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
