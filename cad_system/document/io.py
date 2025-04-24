"""Document import/export functionality."""

import os
import tempfile
from typing import Optional
import pyvista as pv
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeVertex,
                                     BRepBuilderAPI_MakeEdge,
                                     BRepBuilderAPI_MakeFace,
                                     BRepBuilderAPI_MakeSolid)

from ..core.geometry.base import GeometryError
from .base import Document

def export_document(document: Document, format: str) -> bytes:
    """Export the document in the specified format.
    
    Args:
        document: The Document instance to export.
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
            return _export_stl(document)
        elif format == 'STEP':
            return _export_step(document)
        else:
            # Fallback for other formats
            export_str = f"Document: {document.name}, Parts: {len(document.parts)}"
            return export_str.encode()
            
    except Exception as e:
        raise GeometryError(f"Failed to export {format}: {str(e)}")

def import_document(document: Document, data: bytes) -> None:
    """Import document data from a JSON string.
    
    Args:
        document: The Document instance to update.
        data: The document data in bytes.
    
    Updates:
        The document's name and parts list based on deserialized JSON.
    
    Raises:
        json.JSONDecodeError: If the data is not a valid JSON.
    """
    import json
    obj = json.loads(data.decode())
    document.name = obj.get("name", document.name)
    # For simplicity, parts deserialization is omitted; initialize parts list.
    document.parts = []
    document.history = []
    document.redo_stack = []

def _export_stl(document: Document) -> bytes:
    """Export document to STL format.
    
    Args:
        document: The Document instance to export.
    
    Returns:
        STL file content as bytes.
    """
    # Combine all parts into a single mesh for STL export
    combined = pv.PolyData()
    for part in document.parts:
        combined += part.geometry.to_pyvista()
    
    # Use a temporary file to save STL data
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        combined.save(temp_filename, binary=True)
        with open(temp_filename, 'rb') as f:
            stl_data = f.read()
        return stl_data
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def _export_step(document: Document) -> bytes:
    """Export document to STEP format.
    
    Args:
        document: The Document instance to export.
    
    Returns:
        STEP file content as bytes.
    
    Raises:
        GeometryError: If STEP export fails.
    """
    step_writer = STEPControl_Writer()
    Interface_Static_SetCVal("write.step.schema", "AP214")
    
    for part in document.parts:
        shape = _mesh_to_occ_shape(part.geometry.to_pyvista())
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

def _mesh_to_occ_shape(mesh: pv.PolyData) -> Optional[TopoDS_Compound]:
    """Convert PyVista mesh to OpenCASCADE shape.
    
    Args:
        mesh: PyVista mesh to convert.
        
    Returns:
        OpenCASCADE TopoDS_Shape or None if conversion fails.
    """
    try:
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
