import unittest
from cad_system import CADSystem, Part, difference, union, intersection

class TestCADSystem(unittest.TestCase):
    def setUp(self):
        self.cs = CADSystem()
        self.doc = self.cs.new_document("TestDesign")
    
    def test_document_creation(self):
        self.assertEqual(self.doc.name, "TestDesign")
        self.assertEqual(len(self.doc.parts), 0)
    
    def test_part_creation_and_transformation(self):
        box_part = Part.box(10, 20, 30)
        self.assertEqual(box_part.parameters["width"], 10)
        self.assertEqual(box_part.parameters["height"], 20)
        self.assertEqual(box_part.parameters["depth"], 30)
        
        translated = box_part.translate(5, 5, 5)
        self.assertNotEqual(id(box_part), id(translated))
        self.assertEqual(translated.parameters["width"], 10)
    
    def test_boolean_operations(self):
        base = Part.box(20, 30, 10)
        hole = Part.cylinder(5, 10).translate(10, 15, 0)
        
        diff_part = difference(base, hole)
        self.assertEqual(diff_part.parameters["width"], base.parameters["width"])
        
        union_part = union(base, hole)
        self.assertEqual(union_part.parameters["width"], base.parameters["width"])
        
        inter_part = intersection(base, hole)
        self.assertEqual(inter_part.parameters["width"], base.parameters["width"])
    
    def test_document_export(self):
        part = Part.box(15, 25, 35)
        self.doc.add_part(part)
        export_data = self.doc.export("STEP")
        decoded = export_data.decode()
        self.assertIn("TestDesign", decoded)
        self.assertIn("Parts: 1", decoded)
    
    def test_error_export_format(self):
        part = Part.box(10, 20, 30)
        self.doc.add_part(part)
        with self.assertRaises(ValueError):
            self.doc.export("INVALID_FORMAT")

if __name__ == "__main__":
    unittest.main()
