"""
Unit tests for the LLM-Friendly CAD System.
These tests cover PyVista-integrated functionality including geometry creation,
transformations, and Boolean operations.
"""

import unittest
import os
from unittest.mock import patch
import numpy as np
import pyvista as pv
from cad_system import (
    CADSystem, Part, difference, union, intersection,
    GeometryError, GeometryValidationError, BooleanOperationError
)

class TestCADSystem(unittest.TestCase):
    def setUp(self):
        """Initialize test environment."""
        self.cs = CADSystem()
        self.doc = self.cs.new_document("TestDesign")
    
    def test_document_creation(self):
        """Test document creation and initial state."""
        self.assertEqual(self.doc.name, "TestDesign")
        self.assertEqual(len(self.doc.parts), 0)
    
    def test_box_creation(self):
        """Test box primitive creation and mesh generation."""
        box = Part.box(10, 20, 30)
        
        # Test parameters
        self.assertEqual(box.geometry.width, 10)
        self.assertEqual(box.geometry.height, 20)
        self.assertEqual(box.geometry.depth, 30)
        
        # Test PyVista mesh creation
        mesh = box.geometry.to_pyvista()
        self.assertIsInstance(mesh, pv.PolyData)
        
        # Test bounding box
        bounds = mesh.bounds
        self.assertAlmostEqual(bounds[1] - bounds[0], 10)  # width
        self.assertAlmostEqual(bounds[3] - bounds[2], 20)  # height
        self.assertAlmostEqual(bounds[5] - bounds[4], 30)  # depth
    
    def test_cylinder_creation(self):
        """Test cylinder primitive creation and mesh generation."""
        cylinder = Part.cylinder(5, 15)
        
        # Test parameters
        self.assertEqual(cylinder.geometry.radius, 5)
        self.assertEqual(cylinder.geometry.height, 15)
        
        # Test PyVista mesh creation
        mesh = cylinder.geometry.to_pyvista()
        self.assertIsInstance(mesh, pv.PolyData)
        
        # Test bounding box (diameter in x and y)
        bounds = mesh.bounds
        self.assertAlmostEqual(bounds[1] - bounds[0], 10)  # diameter
        self.assertAlmostEqual(bounds[3] - bounds[2], 10)  # diameter
        self.assertAlmostEqual(bounds[5] - bounds[4], 15)  # height
    
    def test_transformations(self):
        """Test geometric transformations."""
        box = Part.box(10, 10, 10)
        
        # Test translation
        translated = box.translate(5, 0, 0)
        mesh = translated.geometry.to_pyvista()
        center = mesh.center
        self.assertAlmostEqual(center[0], 5)  # x coordinate
        
        # Test rotation
        rotated = box.rotate(90, (0, 0, 1))
        self.assertIsInstance(rotated.geometry.to_pyvista(), pv.PolyData)
    
    def test_boolean_operations(self):
        """Test Boolean operations using PyVista."""
        base = Part.box(20, 30, 10)
        hole = Part.cylinder(5, 10).translate(10, 15, 0)
        
        # Test difference (boolean subtraction)
        try:
            result = difference(base, hole)
            self.assertIsInstance(result.geometry.to_pyvista(), pv.PolyData)
            self.assertLess(result.geometry.to_pyvista().volume,
                          base.geometry.to_pyvista().volume)
        except BooleanOperationError as e:
            self.fail(f"Boolean difference failed: {str(e)}")
        
        # Test union
        try:
            result = union(base, hole)
            self.assertIsInstance(result.geometry.to_pyvista(), pv.PolyData)
            combined_volume = (base.geometry.to_pyvista().volume +
                            hole.geometry.to_pyvista().volume)
            self.assertLessEqual(result.geometry.to_pyvista().volume, combined_volume)
        except BooleanOperationError as e:
            self.fail(f"Boolean union failed: {str(e)}")
        
        # Test intersection
        try:
            result = intersection(base, hole)
            self.assertIsInstance(result.geometry.to_pyvista(), pv.PolyData)
            self.assertLess(result.geometry.to_pyvista().volume,
                          base.geometry.to_pyvista().volume)
        except BooleanOperationError as e:
            self.fail(f"Boolean intersection failed: {str(e)}")
    
    def test_invalid_geometries(self):
        """Test error handling for invalid geometries."""
        with self.assertRaises(ValueError):
            Part.box(-1, 10, 10)  # Negative dimension
            
        with self.assertRaises(ValueError):
            Part.cylinder(-5, 10)  # Negative radius
    
    def test_export_formats(self):
        """Test document export functionality."""
        part = Part.box(15, 25, 35)
        self.doc.add_part(part)
        
        # Test STL export
        stl_data = self.doc.export("STL")
        self.assertTrue(len(stl_data) > 0)

        # Test STEP export
        step_data = self.doc.export("STEP")
        self.assertTrue(len(step_data) > 0)
        
        # Verify STEP data contains required elements
        step_str = step_data.decode()
        self.assertTrue("ISO-10303-21" in step_str)
        self.assertTrue("HEADER" in step_str)
        self.assertTrue("DATA" in step_str)
        self.assertTrue("END-ISO-10303-21" in step_str)

        # Test unsupported format
        with self.assertRaises(ValueError):
            self.doc.export("INVALID_FORMAT")

if __name__ == "__main__":
    unittest.main()
