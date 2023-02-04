from typing import Dict, List, Optional, Tuple
import numpy as np
import numpy.typing as npt
from su2fmt.mesh import ElementType, Mesh, Zone 


def parse_mesh(file_path: str):
    with open(file_path, 'r') as file:
        zones = []
        nzone: int = 1

        izone: int = 1
        ndime: Optional[int] = None
        nelem: Optional[int] = None
        npoin: Optional[int] = None
        nmark: int = 0
        points: List[npt.NDArray[np.float32]] = []
        elements: List[npt.NDArray[np.uint16]] = []
        element_types: List[ElementType]  = []
        marker_elements_to_label: Dict[Tuple[int, int], str] = {}
        
        element_index: Optional[int] = None
        point_index: Optional[int] = None
        
        marker_tag: Optional[str] = None
        nmark_elems: Optional[int] = None
        marker_index: Optional[int] = None

        for line in file:
            line = line.strip()

            if line.startswith('NZONE='):
                nzone = int(line.split('=')[1])
            elif line.startswith('NMARK='):
                nmark = int(line.split('=')[1])
            elif line.startswith('IZONE='):
                izone = int(line.split('=')[1])
            
            elif line.startswith('NDIME='):
                if izone > 1:
                    assert ndime is not None, "NDIME must be defined for zone"
                    assert nelem is not None, "NELEM must be defined for zone"
                    assert npoin is not None, "NPOIN must be defined for zone"
                    zone = Zone(izone-1, ndime, nelem, npoin, nmark, elements, element_types, np.array(points), marker_elements_to_label)
                    zones.append(zone)
                ndime = int(line.split('=')[1])
                nelem = None
                npoin = None
                elements = []
                element_types = []
                points = []
                marker_elements_to_label = {}
                element_index = None
                point_index = None
                marker_tag = None
                nmark_elems = None
                marker_index = None

            elif line.startswith('NELEM='):
                nelem = int(line.split('=')[1])
                element_index = 0

            elif line.startswith('NPOIN='):
                npoin = int(line.split('=')[1])
                point_index = 0

            elif line.startswith('MARKER_TAG='):
                marker_tag = line.split('=')[1]
                
            elif line.startswith('MARKER_ELEMS='):
                nmark_elems = int(line.split('=')[1])
                marker_index = 0

            elif element_index is not None:
                assert nelem is not None, "NELEM must be defined for zone before reading elements"
                element = np.array(line.split()[1:-1], dtype=np.uint16)
                element_type = ElementType(int(line.split()[0]))
                elements.append(element)
                element_types.append(element_type)
                if element_index == nelem-1:
                    element_index = None
                else:
                    element_index += 1

            elif point_index is not None:
                assert npoin is not None, "NPOIN must be defined for zone before reading points"
                if ndime == 2:
                    point = np.array(line.split()[:-1]+[0], dtype=np.float32)
                else:
                    point = np.array(line.split()[:-1], dtype=np.float32)
                points.append(point)
                if point_index == npoin-1:
                    point_index = None
                else:
                    point_index += 1


            elif marker_index is not None:
                assert nmark_elems is not None, "MARKER_ELEMS must be defined for zone before reading markers"
                marker_elements = np.array(line.split()[1:], dtype=np.uint16)
                assert marker_tag is not None, "MARKER_TAG must be defined for marker before reading marker elements"
                marker_elements_to_label[(marker_elements[0], marker_elements[1])] = marker_tag
                if marker_index == nmark_elems - 1:
                    marker_index = None
                else:
                    marker_index += 1

        assert ndime is not None, "NDIME must be defined for zone"
        assert nelem is not None, "NELEM must be defined for zone"
        assert npoin is not None, "NPOIN must be defined for zone"
        zone = Zone(izone, ndime, nelem, npoin, nmark, elements, element_types, np.array(points), marker_elements_to_label)
        zones.append(zone)

        return Mesh(nzone, zones)

def combine_meshes(meshes: List[Mesh]):
    zones: List[Zone] = []
    for mesh in meshes:
        zones += mesh.zones
    return Mesh(nzone=len(zones), zones=zones)