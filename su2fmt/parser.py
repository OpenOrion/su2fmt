from typing import Dict, List, Optional
import numpy as np
import numpy.typing as npt
from su2fmt.mesh import SU2Mesh

def parse_mesh(file_path: str) -> SU2Mesh:
    with open(file_path, 'r') as file:
        ndime: Optional[int] = None
        nelem: Optional[int] = None
        npoin: Optional[int] = None
        nmark: int = 0
        points: List[npt.NDArray[np.float32]] = []
        elements: List[npt.NDArray[np.int64]] = []
        element_types: List[int] = []
        markers: Dict[str, List[npt.NDArray[np.int64]]] = {}
        marker_types: Dict[str, List[int]] = {}

        element_index: Optional[int] = None
        point_index: Optional[int] = None
        
        marker_tag: Optional[str] = None
        nmark_elems: Optional[int] = None
        marker_index: Optional[int] = None

        for line in file:
            line = line.strip()

            if line.startswith('NMARK='):
                nmark = int(line.split('=')[1].strip().split()[0])
            elif line.startswith('NDIME='):
                ndime = int(line.split('=')[1].strip().split()[0])
            elif line.startswith('NELEM='):
                nelem = int(line.split('=')[1].strip().split()[0])
                element_index = 0
            elif line.startswith('NPOIN='):
                npoin = int(line.split('=')[1].strip().split()[0])
                point_index = 0
            elif line.startswith('MARKER_TAG='):
                marker_tag = line.split('=')[1].strip()
            elif line.startswith('MARKER_ELEMS='):
                nmark_elems = int(line.split('=')[1].strip().split()[0])
                marker_index = 0

            elif element_index is not None and nelem:
                assert nelem is not None, "NELEM must be defined for zone before reading elements"
                element = np.array(line.split()[1:-1], dtype=np.int64)
                element_type = int(line.split()[0])
                elements.append(element)
                element_types.append(element_type)
                if element_index == nelem-1:
                    element_index = None
                else:
                    element_index += 1

            elif point_index is not None and npoin:
                assert npoin is not None, "NPOIN must be defined for zone before reading points"
                if ndime == 2:
                    point = np.array(line.split()[:2]+[0], dtype=np.float32)
                else:
                    point = np.array(line.split()[:3], dtype=np.float32)
                assert len(point) == 3, "Point must have 3 coordinates"
                points.append(point)
                if point_index == npoin-1:
                    point_index = None
                else:
                    point_index += 1

            elif marker_index is not None:
                assert nmark_elems is not None, "MARKER_ELEMS must be defined for zone before reading markers"
                assert marker_tag is not None, "MARKER_TAG must be defined for marker before reading marker elements"
                
                if marker_tag not in markers:
                    markers[marker_tag] = []
                    marker_types[marker_tag] = []
                
                marker_components = line.split()
                markers[marker_tag].append(
                    np.array(marker_components[1:], dtype=np.int64)
                )
                marker_types[marker_tag].append(int(marker_components[0]))

                if marker_index == nmark_elems - 1:
                    marker_index = None
                else:
                    marker_index += 1

        # Convert to the format expected by SU2Mesh
        assert ndime is not None, "NDIME must be defined"
        assert nelem is not None, "NELEM must be defined"
        assert npoin is not None, "NPOIN must be defined"
        
        # Flatten indices for meshly format
        indices = []
        for elem in elements:
            indices.extend(elem)
        
        # Convert markers to numpy arrays
        mesh_markers = {}
        mesh_marker_types = {}
        
        for marker_tag, marker_elements in markers.items():
            marker_indices = []
            marker_type_values = []
            
            if marker_tag in marker_types:
                for elem, elem_type in zip(marker_elements, marker_types[marker_tag]):
                    marker_indices.extend(elem)
                    marker_type_values.append(elem_type)
            
            if marker_indices:
                mesh_markers[marker_tag] = np.array(marker_indices, dtype=np.int64)
                mesh_marker_types[marker_tag] = np.array(marker_type_values, dtype=np.int32)

        return SU2Mesh(
            vertices=np.array(points),
            indices=np.array(indices, dtype=np.uint32) if indices else None,
            element_types=np.array(element_types, dtype=np.int32),
            markers=mesh_markers,
            marker_types=mesh_marker_types,
            izone=1,
            ndime=ndime
        )

def combine_meshes(meshes: List[SU2Mesh]) -> List[SU2Mesh]:
    """Return list of meshes with updated zone indices."""
    result = []
    for i, mesh in enumerate(meshes, 1):
        # Create a copy with updated izone
        mesh_copy = mesh.model_copy()
        mesh_copy.izone = i
        result.append(mesh_copy)
    return result