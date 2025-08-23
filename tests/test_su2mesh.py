import unittest
import numpy as np
import tempfile
import os
from su2fmt import SU2Mesh, parse_mesh, export_mesh
from su2fmt.mesh import ElementType


class TestSU2Mesh(unittest.TestCase):
    """Test cases for SU2Mesh functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_basic_mesh_creation(self):
        """Test basic SU2Mesh creation and properties."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2], dtype=np.uint32)
        element_types = np.array([ElementType.TRIANGLE.value], dtype=np.int32)
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            izone=1,
            ndime=3
        )
        
        # Test computed properties
        self.assertEqual(mesh.ndime, 3)
        self.assertEqual(mesh.nelem, 1)
        self.assertEqual(mesh.npoin, 3)
        self.assertEqual(mesh.nmark, 0)
        self.assertEqual(mesh.vertex_count, 3)
        self.assertEqual(mesh.index_count, 3)

    def test_2d_mesh_creation(self):
        """Test 2D mesh creation."""
        vertices = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2], dtype=np.uint32)
        element_types = np.array([ElementType.TRIANGLE.value], dtype=np.int32)
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            izone=1,
            ndime=2
        )
        
        self.assertEqual(mesh.ndime, 2)
        self.assertEqual(mesh.npoin, 3)

    def test_mesh_with_markers(self):
        """Test mesh creation with boundary markers."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)
        element_types = np.array([
            ElementType.TRIANGLE.value,
            ElementType.TRIANGLE.value
        ], dtype=np.int32)
        
        markers = {
            "wall": np.array([0, 1, 1, 3], dtype=np.int64),
            "inlet": np.array([0, 2], dtype=np.int64)
        }
        
        marker_types = {
            "wall": np.array([ElementType.LINE.value, ElementType.LINE.value], dtype=np.int32),
            "inlet": np.array([ElementType.LINE.value], dtype=np.int32)
        }
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            markers=markers,
            marker_types=marker_types,
            izone=1,
            ndime=3
        )
        
        self.assertEqual(mesh.nmark, 2)
        self.assertIn("wall", mesh.markers)
        self.assertIn("inlet", mesh.markers)
        self.assertEqual(len(mesh.markers["wall"]), 4)
        self.assertEqual(len(mesh.markers["inlet"]), 2)

    def test_different_element_types(self):
        """Test mesh with different element types."""
        vertices = np.array([
            [0.0, 0.0, 0.0],  # 0
            [1.0, 0.0, 0.0],  # 1
            [0.0, 1.0, 0.0],  # 2
            [1.0, 1.0, 0.0],  # 3
            [0.5, 0.5, 1.0]   # 4
        ], dtype=np.float32)
        
        # Triangle + Tetrahedron
        indices = np.array([0, 1, 2, 0, 1, 2, 4], dtype=np.uint32)
        element_types = np.array([
            ElementType.TRIANGLE.value,
            ElementType.TETRAHEDRON.value
        ], dtype=np.int32)
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            izone=1,
            ndime=3
        )
        
        self.assertEqual(mesh.nelem, 2)
        self.assertEqual(mesh.npoin, 5)

    def test_simple_mesh_parsing(self):
        """Test parsing a simple mesh file."""
        mesh_content = """NDIME= 2
NPOIN= 4
        0.0000000000        0.0000000000 0
        1.0000000000        0.0000000000 1
        1.0000000000        1.0000000000 2
        0.0000000000        1.0000000000 3
NELEM= 2
5 0 1 2 0
5 0 2 3 1
NMARK= 2
MARKER_TAG= wall
MARKER_ELEMS= 2
3 0 1
3 2 3
MARKER_TAG= inlet
MARKER_ELEMS= 1
3 1 2
"""
        
        # Write to temporary file
        mesh_file = os.path.join(self.temp_dir, "test_mesh.su2")
        with open(mesh_file, 'w') as f:
            f.write(mesh_content)
        
        # Parse the mesh
        mesh = parse_mesh(mesh_file)
        
        # Verify parsing results
        self.assertEqual(mesh.ndime, 2)
        self.assertEqual(mesh.nelem, 2)
        self.assertEqual(mesh.npoin, 4)
        self.assertEqual(mesh.nmark, 2)
        
        # Check vertices
        self.assertEqual(mesh.vertices.shape, (4, 3))  # Always 3D internally
        
        # Check elements
        self.assertEqual(len(mesh.element_types), 2)
        self.assertTrue(all(et == ElementType.TRIANGLE.value for et in mesh.element_types))
        
        # Check markers
        self.assertIn("wall", mesh.markers)
        self.assertIn("inlet", mesh.markers)
        self.assertEqual(len(mesh.markers["wall"]), 4)  # 2 lines * 2 vertices each
        self.assertEqual(len(mesh.markers["inlet"]), 2)  # 1 line * 2 vertices

    def test_mesh_with_whitespace_issues(self):
        """Test parsing mesh with whitespace issues (like the original problem)."""
        mesh_content = """NDIME= 3
NPOIN= 4	4
        0.0000000000        0.0000000000        0.0000000000 0
        1.0000000000        0.0000000000        0.0000000000 1
        0.0000000000        1.0000000000        0.0000000000 2
        0.0000000000        0.0000000000        1.0000000000 3
NELEM= 1
10 0 1 2 3 0
NMARK= 1
MARKER_TAG= boundary_face
MARKER_ELEMS= 1
5 0 1 2
"""
        
        mesh_file = os.path.join(self.temp_dir, "whitespace_mesh.su2")
        with open(mesh_file, 'w') as f:
            f.write(mesh_content)
        
        # This should parse without errors despite the whitespace
        mesh = parse_mesh(mesh_file)
        
        self.assertEqual(mesh.ndime, 3)
        self.assertEqual(mesh.npoin, 4)
        self.assertEqual(mesh.nelem, 1)
        self.assertEqual(mesh.nmark, 1)
        self.assertIn("boundary_face", mesh.markers)

    def test_round_trip_parse_export(self):
        """Test round-trip: parse -> export -> parse."""
        original_content = """NDIME= 3
NPOIN= 4
        0.0000000000        0.0000000000        0.0000000000 0
        1.0000000000        0.0000000000        0.0000000000 1
        0.0000000000        1.0000000000        0.0000000000 2
        0.0000000000        0.0000000000        1.0000000000 3
NELEM= 1
10 0 1 2 3 0
NMARK= 1
MARKER_TAG= boundary
MARKER_ELEMS= 1
5 0 1 2
"""
        
        # Write original file
        original_file = os.path.join(self.temp_dir, "original.su2")
        with open(original_file, 'w') as f:
            f.write(original_content)
        
        # Parse
        mesh1 = parse_mesh(original_file)
        
        # Export
        exported_file = os.path.join(self.temp_dir, "exported.su2")
        export_mesh(mesh1, exported_file)
        
        # Parse exported file
        mesh2 = parse_mesh(exported_file)
        
        # Compare meshes
        self.assertEqual(mesh1.ndime, mesh2.ndime)
        self.assertEqual(mesh1.nelem, mesh2.nelem)
        self.assertEqual(mesh1.npoin, mesh2.npoin)
        self.assertEqual(mesh1.nmark, mesh2.nmark)
        
        # Compare vertices (allowing for small floating point differences)
        np.testing.assert_allclose(mesh1.vertices, mesh2.vertices, rtol=1e-6)
        
        # Compare element types
        np.testing.assert_array_equal(mesh1.element_types, mesh2.element_types)
        
        # Compare markers
        for marker_name in mesh1.markers:
            self.assertIn(marker_name, mesh2.markers)
            np.testing.assert_array_equal(
                mesh1.markers[marker_name], 
                mesh2.markers[marker_name]
            )

    def test_meshly_features(self):
        """Test that meshly features work correctly."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2], dtype=np.uint32)
        element_types = np.array([ElementType.TRIANGLE.value], dtype=np.int32)
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            izone=1,
            ndime=3
        )
        
        # Test basic meshly properties
        self.assertEqual(mesh.vertex_count, 3)
        self.assertEqual(mesh.index_count, 3)
        
        # Test model serialization
        mesh_dict = mesh.model_dump()
        self.assertIn("vertices", mesh_dict)
        self.assertIn("indices", mesh_dict)
        self.assertIn("element_types", mesh_dict)
        
        # Test that computed properties are not in the dump (ndime is stored)
        self.assertIn("ndime", mesh_dict)  # ndime is stored field
        self.assertNotIn("nelem", mesh_dict)
        self.assertNotIn("npoin", mesh_dict) 
        self.assertNotIn("nmark", mesh_dict)

    def test_hexahedron_mesh(self):
        """Test mesh with hexahedral elements."""
        # Create a simple cube with one hexahedron
        vertices = np.array([
            [0.0, 0.0, 0.0],  # 0
            [1.0, 0.0, 0.0],  # 1
            [1.0, 1.0, 0.0],  # 2
            [0.0, 1.0, 0.0],  # 3
            [0.0, 0.0, 1.0],  # 4
            [1.0, 0.0, 1.0],  # 5
            [1.0, 1.0, 1.0],  # 6
            [0.0, 1.0, 1.0]   # 7
        ], dtype=np.float32)
        
        # Hexahedron indices (8 vertices)
        indices = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=np.uint32)
        element_types = np.array([ElementType.HEXAHEDRON.value], dtype=np.int32)
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            izone=1,
            ndime=3
        )
        
        self.assertEqual(mesh.nelem, 1)
        self.assertEqual(mesh.npoin, 8)
        self.assertEqual(len(mesh.element_types), 1)
        self.assertEqual(mesh.element_types[0], ElementType.HEXAHEDRON.value)

    def test_empty_mesh(self):
        """Test handling of empty mesh."""
        vertices = np.array([], dtype=np.float32).reshape(0, 3)
        indices = np.array([], dtype=np.uint32)
        element_types = np.array([], dtype=np.int32)
        
        mesh = SU2Mesh(
            vertices=vertices,
            indices=indices,
            element_types=element_types,
            izone=1,
            ndime=3
        )
        
        self.assertEqual(mesh.nelem, 0)
        self.assertEqual(mesh.npoin, 0)
        self.assertEqual(mesh.nmark, 0)


if __name__ == '__main__':
    unittest.main()
