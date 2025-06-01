import os
import numpy as np
from cad_system.part.constraint_base import Entity
from cad_system.part.constraints import DistanceConstraint, AngleConstraint
from cad_system.part.parametric import ConstraintSolver
from cad_system.document.base import create_document_from_geometry
from cad_system.document.io import export_stl
from cad_system.core.geometry.primitives import Points

def create_and_export_box():
    print("\n=== Creating Geometry ===")
    p1 = Entity(position=np.array([0, 0, 0]))
    p2 = Entity(position=np.array([1, 0, 0]))
    p3 = Entity(position=np.array([1, 1, 0]))
    p4 = Entity(position=np.array([0, 1, 0]))
    
    v1 = p2.position - p1.position
    v2 = p3.position - p2.position
    p1.direction = v1 / np.linalg.norm(v1)
    p2.direction = v2 / np.linalg.norm(v2)
    
    print("\n=== Solving Constraints ===")
    solver = ConstraintSolver()
    solver.add_constraint(DistanceConstraint(entities=[p1, p2], parameters={"distance": 1.0}))
    solver.add_constraint(DistanceConstraint(entities=[p2, p3], parameters={"distance": 1.0}))
    solver.add_constraint(AngleConstraint(entities=[p1, p2], parameters={"angle": np.pi/2}))
    
    if solver.solve():
        print("Constraints solved successfully")
        print(f"Final positions:")
        for i, p in enumerate([p1, p2, p3, p4]):
            print(f"p{i+1}: {p.position}")
        
        print("\n=== Creating Document ===")
        points_geom = Points([p.position for p in [p1, p2, p3, p4]])
        doc = create_document_from_geometry([points_geom])
        
        print("\n=== Exporting STL ===")
        vertices, faces = doc.get_mesh_data()
        print(f"Mesh data:")
        print(f"- Vertices: {len(vertices)}")
        print(f"- Faces: {len(faces)}")
        
        filepath = "output/box.stl"
        if export_stl(doc, filepath):
            print(f"\nSuccessfully exported to {filepath}")
            print(f"File size: {os.path.getsize(filepath)} bytes")
            return True
    
    return False

if __name__ == "__main__":
    create_and_export_box()