from typing import Any, Dict, List, Optional, Tuple

class Geometry:
    """Abstract Geometry base class defining core API for all geometric primitives."""
    def bounding_box(self) -> Tuple[float, float, float]:
        raise NotImplementedError("bounding_box() must be implemented by subclasses.")

    def translate(self, x: float, y: float, z: float) -> "Geometry":
        raise NotImplementedError("translate() must be implemented by subclasses.")

    def rotate(self, angle: float, axis: Tuple[float, float, float]) -> "Geometry":
        raise NotImplementedError("rotate() must be implemented by subclasses.")

    def clone(self) -> "Geometry":
        raise NotImplementedError("clone() must be implemented by subclasses.")

class Box(Geometry):
    def __init__(self, width: float, height: float, depth: float) -> None:
        self.width = width
        self.height = height
        self.depth = depth

    def bounding_box(self) -> Tuple[float, float, float]:
        return (self.width, self.height, self.depth)

    def translate(self, x: float, y: float, z: float) -> "Box":
        return Box(self.width, self.height, self.depth)

    def rotate(self, angle: float, axis: Tuple[float, float, float]) -> "Box":
        return Box(self.width, self.height, self.depth)

    def clone(self) -> "Box":
        return Box(self.width, self.height, self.depth)

class Cylinder(Geometry):
    def __init__(self, radius: float, height: float) -> None:
        self.radius = radius
        self.height = height

    def bounding_box(self) -> Tuple[float, float, float]:
        return (self.radius * 2, self.radius * 2, self.height)

    def translate(self, x: float, y: float, z: float) -> "Cylinder":
        return Cylinder(self.radius, self.height)

    def rotate(self, angle: float, axis: Tuple[float, float, float]) -> "Cylinder":
        return Cylinder(self.radius, self.height)

    def clone(self) -> "Cylinder":
        return Cylinder(self.radius, self.height)

class Part:
    def __init__(self, name: str, geometry: Geometry, parameters: Optional[Dict[str, Any]] = None) -> None:
        self.name: str = name
        self.geometry: Geometry = geometry
        self.parameters: Dict[str, Any] = parameters if parameters is not None else {}
    
    @staticmethod
    def box(width: float, height: float, depth: float) -> "Part":
        geometry = Box(width, height, depth)
        return Part("Box", geometry, {"width": width, "height": height, "depth": depth})
    
    @staticmethod
    def cylinder(radius: float, height: float) -> "Part":
        geometry = Cylinder(radius, height)
        return Part("Cylinder", geometry, {"radius": radius, "height": height})
    
    def translate(self, x: float, y: float, z: float) -> "Part":
        new_geometry = self.geometry.translate(x, y, z)
        return Part(self.name, new_geometry, self.parameters.copy())
    
    def rotate(self, angle: float, axis: Tuple[float, float, float]) -> "Part":
        new_geometry = self.geometry.rotate(angle, axis)
        return Part(self.name, new_geometry, self.parameters.copy())
    
    def clone(self) -> "Part":
        return Part(self.name, self.geometry.clone(), self.parameters.copy())
    
    def parameterize(self) -> "ParametricPart":
        return ParametricPart(self)

class ParametricPart:
    def __init__(self, part: Part) -> None:
        self.part: Part = part
        self.constraints: List[Tuple[str, str, str]] = []
    
    def add_constraint(self, param1: str, param2: str, relation: str) -> None:
        self.constraints.append((param1, param2, relation))
    
    def update_parameters(self, params: Dict[str, float]) -> None:
        self.part.parameters.update(params)
    
    def solve(self) -> bool:
        for (p1, p2, relation) in self.constraints:
            if relation == "equal":
                if p1 in self.part.parameters:
                    self.part.parameters[p2] = self.part.parameters[p1]
                elif p2 in self.part.parameters:
                    self.part.parameters[p1] = self.part.parameters[p2]
        return True

class Document:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.parts: List[Part] = []
        self.history: List[Any] = []
        self.redo_stack: List[Any] = []
    
    def add_part(self, part: Part) -> None:
        self.parts.append(part)
        self.history.append(("add", part))
    
    def get_part(self, name: str) -> Optional[Part]:
        for p in self.parts:
            if p.name == name:
                return p
        return None
    
    def export(self, format: str) -> bytes:
        supported_formats = {"STEP", "STL", "OBJ", "DXF"}
        if format not in supported_formats:
            raise ValueError(f"Format {format} is not supported.")
        export_str = f"Document: {self.name}, Parts: {len(self.parts)}"
        return export_str.encode()
    
    def import_(self, data: bytes) -> None:
        import json
        obj = json.loads(data.decode())
        self.name = obj.get("name", self.name)
        self.parts = []
        self.history = []
        self.redo_stack = []
    
    def undo(self) -> Any:
        if not self.history:
            raise RuntimeError("No actions to undo.")
        action = self.history.pop()
        if action[0] == "add":
            part = action[1]
            if part in self.parts:
                self.parts.remove(part)
        self.redo_stack.append(action)
        return action
    
    def redo(self) -> None:
        if not self.redo_stack:
            raise RuntimeError("No actions to redo.")
        action = self.redo_stack.pop()
        if action[0] == "add":
            part = action[1]
            self.parts.append(part)
        self.history.append(action)

    def visualize(self) -> None:
        print(f"Visualizing Document: {self.name} with {len(self.parts)} parts")

class CADSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config if config is not None else {}
        self.version: str = "1.0.0"
    
    def new_document(self, name: str) -> Document:
        if not name:
            raise ValueError("Document name must not be empty.")
        return Document(name)
    
    def load_document(self, path: str) -> Document:
        import json
        with open(path, "r") as f:
            data = json.load(f)
        doc = Document(data["name"])
        return doc

def union(a: Part, b: Part) -> Part:
    print("Performing union operation (stub).")
    result = a.clone()
    result.parameters["operation"] = "union"
    return result

def difference(a: Part, b: Part) -> Part:
    print("Performing difference operation (stub).")
    result = a.clone()
    result.parameters["operation"] = "difference"
    return result

def intersection(a: Part, b: Part) -> Part:
    print("Performing intersection operation (stub).")
    result = a.clone()
    result.parameters["operation"] = "intersection"
    return result

def main() -> None:
    cs = CADSystem()
    doc = cs.new_document("MyDesign")
    base = Part.box(20, 30, 10)
    hole = Part.cylinder(5, 10).translate(10, 15, 0)
    result = difference(base, hole)
    doc.add_part(result)
    exported_data = doc.export("STEP")
    print(exported_data.decode())
    doc.visualize()

if __name__ == "__main__":
    main()
