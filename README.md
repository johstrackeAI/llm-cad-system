# Python CAD System

A modular Computer-Aided Design (CAD) system implemented in Python, offering parametric 3D modeling capabilities with a focus on geometric primitives and boolean operations.

## Package Structure

```
cad_system/
├── __init__.py
├── system.py
├── core/
│   ├── geometry/
│   │   ├── base.py
│   │   ├── primitives.py
│   │   └── types.py
│   └── operations/
│       ├── boolean.py
│       └── transforms.py
├── document/
│   ├── base.py
│   ├── io.py
│   └── visualization.py
└── part/
    ├── base.py
    └── parametric.py
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-cad-system.git
cd python-cad-system
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate cad-system
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Basic Usage

```python
from cad_system.core.geometry import primitives
from cad_system.core.operations import boolean, transforms
from cad_system.document import visualization

# Create basic shapes
cube = primitives.Box(width=10, height=10, depth=10)
sphere = primitives.Sphere(radius=6)

# Apply boolean operation
result = boolean.difference(cube, sphere)

# Transform the result
transformed = transforms.rotate(result, axis='z', angle=45)

# Visualize
doc = visualization.create_document(transformed)
doc.show()
```

## Development Setup

1. Install additional development dependencies:
```bash
pip install pytest pytest-cov black isort mypy
```

2. Run tests:
```bash
pytest tests/
```

3. Format code:
```bash
black .
isort .
```

4. Run type checking:
```bash
mypy cad_system/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
