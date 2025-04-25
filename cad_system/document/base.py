from typing import List, Tuple
import numpy as np
from ..core.geometry.primitives import Points
from ..core.geometry.base import Entity

class Edge:
    def __init__(self, points: List[np.ndarray]):
        self.points = points

class Document:
    def __init__(self):
        self.geometry = []
        self.parts = []
        self.entities = []
        
    def add_geometry(self, geom: Entity) -> None:
        self.geometry.append(geom)
        
    def get_mesh_data(self) -> Tuple[np.ndarray, np.ndarray]:
        vertices = []
        faces = []
        
        for geom in self.geometry:
            if isinstance(geom, Points):
                vert_start = len(vertices)
                for point in geom.positions:
                    vertices.append(point)
                
                if len(vertices) >= 3:
                    for i in range(len(vertices) - 2):
                        faces.append([vert_start, vert_start + i + 1, vert_start + i + 2])
        
        return np.array(vertices), np.array(faces)

def create_document_from_geometry(geometry_list: List[Entity]) -> Document:
    doc = Document()
    for geom in geometry_list:
        doc.add_geometry(geom)
    return doc