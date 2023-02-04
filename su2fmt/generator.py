from typing import List
from su2fmt.mesh import Mesh, Zone

ELEMENT_INDENT = " " * 2

def generate_mesh(mesh: Mesh, file_path: str):
    with open(file_path, 'w+') as file:
        if mesh.nzone > 1:
            file.write(f"NZONE= {mesh.nzone}\n")
        spaces = " " * 8
        for zone in mesh.zones:
            if mesh.nzone > 1:
                file.write(f"IZONE= {zone.izone}\n")
            file.write(f"NDIME= {zone.ndime}\n")
            file.write(f"NPOIN= {zone.npoin}\n")
            for index, point in enumerate(zone.points):
                point_row = [*(point[:-1] if zone.ndime == 2 else point), index]
                file.write(f"{spaces}{spaces.join(map(str, point_row))}\n")

            file.write(f"NELEM= {zone.nelem}\n")
            for index, element in enumerate(zone.elements):
                element_row = [zone.element_types[index].value, *element, index]
                file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")

            file.write(f"NMARK= {zone.nmark}\n")
            for marker in zone.markers:
                file.write(f"MARKER_TAG={marker.tag}\n")
                file.write(f"MARKER_ELEMS= {marker.nelem}\n")
                for index, element in enumerate(marker.elements):
                    element_row = [3, *element]
                    file.write(f"{ELEMENT_INDENT}{spaces.join(map(str, element_row))}\n")
