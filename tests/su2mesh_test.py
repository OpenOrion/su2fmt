import unittest
import numpy as np
import tempfile
import os
from typing import List
from su2fmt import parse_mesh, export_mesh, SU2ElementType
from meshly import Mesh


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
        """Test basic Mesh creation and properties."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2], dtype=np.uint32)
        cell_types = np.array([SU2ElementType.TRIANGLE.value], dtype=np.uint32)
        index_sizes = np.array([3], dtype=np.uint32)
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            cell_types=cell_types,
            index_sizes=index_sizes,
            dim=3
        )
        
        # Test computed properties
        self.assertEqual(mesh.dim, 3)
        self.assertEqual(mesh.polygon_count, 1)
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
        cell_types = np.array([SU2ElementType.TRIANGLE.value], dtype=np.uint32)
        index_sizes = np.array([3], dtype=np.uint32)
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            cell_types=cell_types,
            index_sizes=index_sizes,
            dim=2
        )
        
        self.assertEqual(mesh.dim, 2)
        self.assertEqual(mesh.vertex_count, 3)

    def test_mesh_with_markers(self):
        """Test mesh creation with boundary markers."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)
        cell_types = np.array([
            SU2ElementType.TRIANGLE.value,
            SU2ElementType.TRIANGLE.value
        ], dtype=np.uint32)
        index_sizes = np.array([3, 3], dtype=np.uint32)
        
        markers = {
            "wall": [[0, 1], [1, 3]],
            "inlet": [[0, 2]]
        }
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            cell_types=cell_types,
            index_sizes=index_sizes,
            markers=markers,
            dim=3
        )
        
        self.assertEqual(len(mesh.markers), 2)
        self.assertIn("wall", mesh.markers)
        self.assertIn("inlet", mesh.markers)
        reconstructed = mesh.get_reconstructed_markers()
        self.assertEqual(len(reconstructed["wall"]), 2)
        self.assertEqual(len(reconstructed["inlet"]), 1)

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
        cell_types = np.array([
            SU2ElementType.TRIANGLE.value,
            SU2ElementType.TETRAHEDRON.value
        ], dtype=np.uint32)
        index_sizes = np.array([3, 4], dtype=np.uint32)
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            cell_types=cell_types,
            index_sizes=index_sizes,
            dim=3
        )
        
        self.assertEqual(mesh.polygon_count, 2)
        self.assertEqual(mesh.vertex_count, 5)

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
        assert isinstance(mesh, Mesh), "Parsed mesh should be an instance of Mesh"
        
        # Verify parsing results
        self.assertEqual(mesh.dim, 2)
        self.assertEqual(mesh.polygon_count, 2)
        self.assertEqual(mesh.vertex_count, 4)
        self.assertEqual(len(mesh.markers), 2)
        
        # Check vertices
        self.assertEqual(mesh.vertices.shape, (4, 3))  # Always 3D internally
        
        # Check elements
        self.assertEqual(len(mesh.cell_types), 2)
        self.assertTrue(all(et == SU2ElementType.TRIANGLE.value for et in mesh.cell_types))
        
        # Check markers
        self.assertIn("wall", mesh.markers)
        self.assertIn("inlet", mesh.markers)
        reconstructed = mesh.get_reconstructed_markers()
        self.assertEqual(len(reconstructed["wall"]), 2)  # 2 lines
        self.assertEqual(len(reconstructed["inlet"]), 1)  # 1 line

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
        assert isinstance(mesh, Mesh), "Parsed mesh should be an instance of Mesh"
        self.assertEqual(mesh.dim, 3)
        self.assertEqual(mesh.vertex_count, 4)
        self.assertEqual(mesh.polygon_count, 1)
        self.assertEqual(len(mesh.markers), 1)
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
        assert isinstance(mesh1, Mesh), "Parsed mesh should be an instance of Mesh"
        # Export
        exported_file = os.path.join(self.temp_dir, "exported.su2")
        export_mesh(mesh1, exported_file)
        
        # Parse exported file
        mesh2 = parse_mesh(exported_file)
        assert isinstance(mesh2, Mesh), "Parsed mesh should be an instance of Mesh"
        # Compare meshes
        self.assertEqual(mesh1.dim, mesh2.dim)
        self.assertEqual(mesh1.polygon_count, mesh2.polygon_count)
        self.assertEqual(mesh1.vertex_count, mesh2.vertex_count)
        self.assertEqual(len(mesh1.markers), len(mesh2.markers))
        
        # Compare vertices (allowing for small floating point differences)
        np.testing.assert_allclose(mesh1.vertices, mesh2.vertices, rtol=1e-6)
        
        # Compare cell types
        np.testing.assert_array_equal(mesh1.cell_types, mesh2.cell_types)
        
        # Compare markers
        markers1 = mesh1.get_reconstructed_markers()
        markers2 = mesh2.get_reconstructed_markers()
        for marker_name in markers1:
            self.assertIn(marker_name, markers2)
            self.assertEqual(len(markers1[marker_name]), len(markers2[marker_name]))

    def test_meshly_features(self):
        """Test that meshly features work correctly."""
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2], dtype=np.uint32)
        cell_types = np.array([SU2ElementType.TRIANGLE.value], dtype=np.uint32)
        index_sizes = np.array([3], dtype=np.uint32)
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            cell_types=cell_types,
            index_sizes=index_sizes,
            dim=3
        )
        
        # Test basic meshly properties
        self.assertEqual(mesh.vertex_count, 3)
        self.assertEqual(mesh.index_count, 3)
        self.assertEqual(mesh.polygon_count, 1)
        
        # Test model serialization
        mesh_dict = mesh.model_dump()
        self.assertIn("vertices", mesh_dict)
        self.assertIn("indices", mesh_dict)
        self.assertIn("cell_types", mesh_dict)
        self.assertIn("dim", mesh_dict)

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
        cell_types = np.array([SU2ElementType.HEXAHEDRON.value], dtype=np.uint32)
        index_sizes = np.array([8], dtype=np.uint32)
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            cell_types=cell_types,
            index_sizes=index_sizes,
            dim=3
        )
        
        self.assertEqual(mesh.polygon_count, 1)
        self.assertEqual(mesh.vertex_count, 8)
        self.assertEqual(len(mesh.cell_types), 1)
        self.assertEqual(mesh.cell_types[0], SU2ElementType.HEXAHEDRON.value)

    def test_empty_mesh(self):
        """Test handling of empty mesh."""
        vertices = np.array([], dtype=np.float32).reshape(0, 3)
        indices = np.array([], dtype=np.uint32)
        
        mesh = Mesh(
            vertices=vertices,
            indices=indices,
            dim=3
        )
        
        self.assertEqual(mesh.vertex_count, 0)
        self.assertEqual(mesh.index_count, 0)

    def test_multizone_parsing(self):
        """Test parsing of multizone mesh files."""
        multizone_content = """NZONE= 2

IZONE= 1
NDIME= 2
NELEM= 2
5 0 1 2 0
5 0 2 3 1
NPOIN= 4
0.0 0.0 0
1.0 0.0 1
1.0 1.0 2
0.0 1.0 3
NMARK= 1
MARKER_TAG= wall1
MARKER_ELEMS= 2
3 0 1
3 2 3

IZONE= 2
NDIME= 2
NELEM= 1
5 0 1 2 0
NPOIN= 3
2.0 0.0 0
3.0 0.0 1
2.5 1.0 2
NMARK= 1
MARKER_TAG= wall2
MARKER_ELEMS= 1
3 0 1
"""
        
        # Write to temporary file
        mesh_file = os.path.join(self.temp_dir, "multizone_mesh.su2")
        with open(mesh_file, 'w') as f:
            f.write(multizone_content)
        
        # Parse the mesh
        result = parse_mesh(mesh_file)
        assert isinstance(result, List), "Parsed result should be a list of Mesh"
        
        # Should return a list of meshes
        self.assertIsInstance(result, list, "Multizone mesh should return a list")
        self.assertEqual(len(result), 2, "Should have 2 zones")
        
        # Check first zone
        zone1 = result[0]
        self.assertIsInstance(zone1, Mesh, "Zone 1 should be Mesh")
        self.assertEqual(zone1.dim, 2, "Zone 1 dim should be 2")
        self.assertEqual(zone1.polygon_count, 2, "Zone 1 should have 2 elements")
        self.assertEqual(zone1.vertex_count, 4, "Zone 1 should have 4 points")
        self.assertEqual(len(zone1.markers), 1, "Zone 1 should have 1 marker")
        self.assertIn('wall1', zone1.markers, "Zone 1 should have wall1 marker")
        
        # Check second zone
        zone2 = result[1]
        self.assertIsInstance(zone2, Mesh, "Zone 2 should be Mesh")
        self.assertEqual(zone2.dim, 2, "Zone 2 dim should be 2")
        self.assertEqual(zone2.polygon_count, 1, "Zone 2 should have 1 element")
        self.assertEqual(zone2.vertex_count, 3, "Zone 2 should have 3 points")
        self.assertEqual(len(zone2.markers), 1, "Zone 2 should have 1 marker")
        self.assertIn('wall2', zone2.markers, "Zone 2 should have wall2 marker")

    def test_single_zone_backward_compatibility(self):
        """Test that single zone files still work (backward compatibility)."""
        # This test uses the existing simple mesh content from test_simple_mesh_parsing
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
        mesh_file = os.path.join(self.temp_dir, "single_zone_mesh.su2")
        with open(mesh_file, 'w') as f:
            f.write(mesh_content)
        
        # Parse the mesh
        result = parse_mesh(mesh_file)
        assert isinstance(result, Mesh), "Parsed mesh should be an instance of Mesh"
        # Should return a single mesh, not a list
        self.assertIsInstance(result, Mesh, "Single zone mesh should return Mesh directly")
        self.assertEqual(result.dim, 2, "Single zone dim should be 2")
        self.assertEqual(result.polygon_count, 2, "Single zone should have 2 elements")
        self.assertEqual(result.vertex_count, 4, "Single zone should have 4 points")
        self.assertEqual(len(result.markers), 2, "Single zone should have 2 markers")
        self.assertIn('wall', result.markers, "Single zone should have wall marker")
        self.assertIn('inlet', result.markers, "Single zone should have inlet marker")

    def test_multizone_with_different_dimensions(self):
        """Test multizone mesh with zones having different dimensions."""
        multizone_mixed_content = """NZONE= 2

IZONE= 1
NDIME= 2
NELEM= 1
5 0 1 2 0
NPOIN= 3
0.0 0.0 0
1.0 0.0 1
0.5 1.0 2
NMARK= 1
MARKER_TAG= boundary2d
MARKER_ELEMS= 1
3 0 1

IZONE= 2
NDIME= 3
NELEM= 1
10 0 1 2 3 0
NPOIN= 4
0.0 0.0 0.0 0
1.0 0.0 0.0 1
0.5 1.0 0.0 2
0.5 0.5 1.0 3
NMARK= 1
MARKER_TAG= boundary3d
MARKER_ELEMS= 1
5 0 1 2
"""
        
        # Write to temporary file
        mesh_file = os.path.join(self.temp_dir, "mixed_dimension_mesh.su2")
        with open(mesh_file, 'w') as f:
            f.write(multizone_mixed_content)
        
        # Parse the mesh
        result = parse_mesh(mesh_file)
        assert isinstance(result, list), "Parsed result should be a list of Mesh"
        
        # Should return a list of meshes
        self.assertIsInstance(result, list, "Multizone mesh should return a list")
        self.assertEqual(len(result), 2, "Should have 2 zones")
        
        # Check 2D zone
        zone1 = result[0]
        self.assertEqual(zone1.dim, 2, "Zone 1 should be 2D")
        self.assertEqual(zone1.polygon_count, 1, "Zone 1 should have 1 element")
        self.assertIn('boundary2d', zone1.markers, "Zone 1 should have boundary2d marker")
        
        # Check 3D zone
        zone2 = result[1]
        self.assertEqual(zone2.dim, 3, "Zone 2 should be 3D")
        self.assertEqual(zone2.polygon_count, 1, "Zone 2 should have 1 element")
        self.assertIn('boundary3d', zone2.markers, "Zone 2 should have boundary3d marker")


if __name__ == '__main__':
    unittest.main()
