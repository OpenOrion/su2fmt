import numpy.typing as npt
from typing import List
import numpy as np
from su2fmt.mesh import ElementType, Mesh

ELEMENT_INDENT = " " * 2

def get_unused_point_indexes(points: npt.NDArray[np.float64], elements: List[npt.NDArray[np.uint16]]):
    used_point_indexes = set()
    point_indexes = set(range(len(points)))
    for element in elements:
        for point_index in element:
            used_point_indexes.add(point_index)
    return point_indexes.difference(used_point_indexes)

def export_mesh(mesh: Mesh, file_path: str):
    with open(file_path, 'w+') as file:
        if mesh.nzone > 1:
            file.write(f"NZONE= {mesh.nzone}\n")
        spaces = " " * 8
        for zone in mesh.zones:
            unused_point_indexes = get_unused_point_indexes(zone.points, zone.elements)
            if mesh.nzone > 1:
                file.write(f"IZONE= {zone.izone}\n")
            file.write(f"NDIME= {zone.ndime}\n")
            file.write(f"NPOIN= {zone.npoin-len(unused_point_indexes)}\n")
            for index, point in enumerate(zone.points):
                if index in unused_point_indexes:
                    continue
                point_row = [*(point[:-1] if zone.ndime == 2 else point), index]
                file.write(f"{spaces}{spaces.join(map(str, point_row))}\n")

            file.write(f"NELEM= {zone.nelem}\n")
            for index, element in enumerate(zone.elements):
                element_row = [zone.element_types[index].value, *element, index]
                file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")

            file.write(f"NMARK= {zone.nmark}\n")
            for marker_tag, marker_elements in zone.markers.items():
                file.write(f"MARKER_TAG={marker_tag}\n")
                file.write(f"MARKER_ELEMS= {len(marker_elements)}\n")
                for index, element in enumerate(marker_elements):
                    if not len(zone.marker_types.values()):
                        assert len(element) == 2, "marker types must be passed for non-lines, only accepting no markers for backwards compatibility"
                        marker_type = ElementType.LINE.value
                    else:
                        marker_type = zone.marker_types[marker_tag][index].value
                    element_row = [marker_type, *element]
                    file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")
