import numpy.typing as npt
from typing import List
import numpy as np
from su2fmt.mesh import ElementType, SU2Mesh

ELEMENT_INDENT = " " * 2

def get_element_vertex_count(element_type: int) -> int:
    """Get the number of vertices for a given element type."""
    if element_type == ElementType.LINE.value:
        return 2
    elif element_type == ElementType.TRIANGLE.value:
        return 3
    elif element_type == ElementType.QUADRILATERAL.value:
        return 4
    elif element_type == ElementType.TETRAHEDRON.value:
        return 4
    elif element_type == ElementType.HEXAHEDRON.value:
        return 8
    elif element_type == ElementType.PRISM.value:
        return 6
    elif element_type == ElementType.PYRAMID.value:
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

def export_mesh(mesh: SU2Mesh, file_path: str):
    """Export a single SU2Mesh to a file."""
    with open(file_path, 'w+') as file:
        spaces = " " * 8
        
        # Write zone header if needed
        file.write(f"NDIME= {mesh.ndime}\n")
        
        # Write points
        unused_point_indexes = get_unused_point_indexes(mesh.vertices, mesh.indices) if mesh.indices is not None else set()
        npoin = mesh.npoin if mesh.npoin is not None else len(mesh.vertices)
        file.write(f"NPOIN= {npoin - len(unused_point_indexes)}\n")
        
        for index, point in enumerate(mesh.vertices):
            if index in unused_point_indexes:
                continue
            point_row = [*(point[:-1] if mesh.ndime == 2 else point), index]
            file.write(f"{spaces}{spaces.join(map(str, point_row))}\n")

        # Write elements
        file.write(f"NELEM= {mesh.nelem}\n")
        if mesh.indices is not None:
            # Reconstruct elements from flattened indices and element types
            idx = 0
            element_index = 0
            for elem_type in mesh.element_types:
                num_vertices = get_element_vertex_count(elem_type)
                element_vertices = mesh.indices[idx:idx + num_vertices]
                element_row = [elem_type, *element_vertices, element_index]
                file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")
                
                idx += num_vertices
                element_index += 1

        # Write markers
        file.write(f"NMARK= {mesh.nmark}\n")
        for marker_tag, marker_indices in mesh.markers.items():
            file.write(f"MARKER_TAG= {marker_tag}\n")
            
            # Count number of marker elements
            marker_types_for_tag = mesh.marker_types.get(marker_tag, [])
            if len(marker_types_for_tag) > 0:
                num_marker_elems = len(marker_types_for_tag)
            else:
                # Assume all are lines if no types specified
                num_marker_elems = len(marker_indices) // 2
            
            file.write(f"MARKER_ELEMS= {num_marker_elems}\n")
            
            # Write marker elements
            idx = 0
            for i in range(num_marker_elems):
                if len(marker_types_for_tag) > 0:
                    marker_type = marker_types_for_tag[i]
                    num_vertices = get_element_vertex_count(marker_type)
                else:
                    marker_type = ElementType.LINE.value
                    num_vertices = get_element_vertex_count(marker_type)
                
                element_vertices = marker_indices[idx:idx + num_vertices]
                element_row = [marker_type, *element_vertices]
                file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")
                
                idx += num_vertices
