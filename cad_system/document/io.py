import numpy as np
from typing import List, Tuple
from ..core.geometry.primitives import Points
from .base import Document

def create_document_from_geometry(points: List['Entity']) -> Document:
    doc = Document()
    positions = [p.position for p in points]
    doc.add_geometry(Points(positions))
    return doc

def export_stl(doc: Document, filepath: str) -> bool:
    vertices, faces = doc.get_mesh_data()
    if len(vertices) == 0 or len(faces) == 0:
        print("Warning: No mesh data to write!")
        return False
        
    normals = []
    for face in faces:
        v1, v2, v3 = vertices[face]
        normal = np.cross(v2 - v1, v3 - v1)
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal = normal / norm
        normals.append(normal)
    
    try:
        with open(filepath, 'wb') as f:
            f.write(b'\0' * 80)
            f.write(len(faces).to_bytes(4, 'little'))
            
            for normal, face in zip(normals, faces):
                f.write(normal.astype(np.float32).tobytes())
                for idx in face:
                    f.write(vertices[idx].astype(np.float32).tobytes())
                f.write(b'\0\0')
        return True
    except Exception as e:
        print(f"Error writing STL file: {e}")
        return False