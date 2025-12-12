import numpy.typing as npt
from typing import List
import numpy as np
from meshly import Mesh
from su2fmt.types import SU2ElementType, VTK_TO_SU2_MAPPING

ELEMENT_INDENT = " " * 2

def get_element_vertex_count(element_type: int) -> int:
    """Get the number of vertices for a given element type."""
    if element_type == SU2ElementType.LINE.value:
        return 2
    elif element_type == SU2ElementType.TRIANGLE.value:
        return 3
    elif element_type == SU2ElementType.QUADRILATERAL.value:
        return 4
    elif element_type == SU2ElementType.TETRAHEDRON.value:
        return 4
    elif element_type == SU2ElementType.HEXAHEDRON.value:
        return 8
    elif element_type == SU2ElementType.PRISM.value:
        return 6
    elif element_type == SU2ElementType.PYRAMID.value:
        return 5
    else:
        raise ValueError(f"Unknown element type: {element_type}")

def get_unused_point_indexes(points: npt.NDArray[np.float64], indices: npt.NDArray[np.int64]):
    """Find unused point indexes in the mesh."""
    used_point_indexes = set()
    point_indexes = set(range(len(points)))
    for point_index in indices:
        used_point_indexes.add(point_index)
    return point_indexes.difference(used_point_indexes)

def export_mesh(mesh: Mesh, file_path: str):
    """Export a meshly.Mesh to SU2 format file."""
    with open(file_path, 'w+') as file:
        spaces = " " * 8
        
        # Get dimension from mesh
        ndime = mesh.dim if hasattr(mesh, 'dim') else 3
        
        # Write zone header
        file.write(f"NDIME= {ndime}\n")
        
        # Write points
        unused_point_indexes = get_unused_point_indexes(mesh.vertices, np.asarray(mesh.indices)) if mesh.indices is not None and len(mesh.indices) > 0 else set()
        npoin = len(mesh.vertices)
        file.write(f"NPOIN= {npoin - len(unused_point_indexes)}\n")
        
        for index, point in enumerate(mesh.vertices):
            if index in unused_point_indexes:
                continue
            point_row = [*(point[:-1] if ndime == 2 else point), index]
            file.write(f"{spaces}{spaces.join(map(str, point_row))}\n")

        # Write elements
        nelem = mesh.polygon_count if mesh.indices is not None and len(mesh.indices) > 0 else 0
        file.write(f"NELEM= {nelem}\n")
        
        if mesh.indices is not None and len(mesh.indices) > 0 and mesh.cell_types is not None:
            # Reconstruct elements from flattened indices using index_sizes
            idx = 0
            element_index = 0
            
            for i, vtk_type in enumerate(mesh.cell_types):
                if mesh.index_sizes is not None:
                    num_vertices = mesh.index_sizes[i]
                else:
                    num_vertices = get_element_vertex_count(int(vtk_type))
                
                # Convert VTK cell type to SU2 element type
                su2_type = VTK_TO_SU2_MAPPING.get(int(vtk_type), int(vtk_type))
                
                element_vertices = mesh.indices[idx:idx + num_vertices]
                element_row = [su2_type, *element_vertices, element_index]
                file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")
                
                idx += num_vertices
                element_index += 1

        # Write markers
        nmark = len(mesh.markers) if hasattr(mesh, 'markers') and mesh.markers else 0
        file.write(f"NMARK= {nmark}\n")
        
        # Get reconstructed markers (list-of-lists format)
        reconstructed_markers = mesh.get_reconstructed_markers() if hasattr(mesh, 'get_reconstructed_markers') else mesh.markers
        
        for marker_tag, marker_elements in reconstructed_markers.items():
            file.write(f"MARKER_TAG= {marker_tag}\n")
            
            # Number of marker elements
            num_marker_elems = len(marker_elements)
            file.write(f"MARKER_ELEMS= {num_marker_elems}\n")
            
            # Get marker cell types if available
            marker_cell_types = mesh.marker_cell_types.get(marker_tag) if hasattr(mesh, 'marker_cell_types') else None
            
            # Write marker elements
            for i, element_vertices in enumerate(marker_elements):
                if marker_cell_types is None or i >= len(marker_cell_types):
                    raise ValueError(
                        f"Missing cell type information for marker '{marker_tag}' element {i}. "
                        f"Marker has {len(marker_elements)} elements but cell_types has "
                        f"{len(marker_cell_types) if marker_cell_types else 0} entries."
                    )
                
                # Convert VTK cell type to SU2 element type
                su2_marker_type = VTK_TO_SU2_MAPPING.get(int(marker_cell_types[i]), int(marker_cell_types[i]))
                
                element_row = [su2_marker_type, *element_vertices]
                file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")
