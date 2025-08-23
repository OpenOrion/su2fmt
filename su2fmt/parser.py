from typing import Dict, List, Optional, Tuple
import numpy as np
import numpy.typing as npt
from su2fmt.mesh import ElementType, Mesh, Zone 
import dataclasses

def parse_mesh(file_path: str):
    with open(file_path, 'r') as file:
        zones = []
        nzone: int = 1

        izone_len = 0
        izone: int = 0
        ndime: Optional[int] = None
        nelem: Optional[int] = None
        npoin: Optional[int] = None
        nmark: int = 0
        points: List[npt.NDArray[np.float32]] = []
        elements: List[npt.NDArray[np.int64]] = []
        element_types: List[ElementType]  = []
        markers: Dict[str, List[npt.NDArray[np.int64]]] = {}
        marker_types: Dict[str, List[ElementType]] = {}

        element_index: Optional[int] = None
        point_index: Optional[int] = None
        
        marker_tag: Optional[str] = None
        nmark_elems: Optional[int] = None
        marker_index: Optional[int] = None

        for line in file:
            line = line.strip()

            if line.startswith('NZONE='):
                nzone = int(line.split('=')[1].strip().split()[0])
            elif line.startswith('NMARK='):
                nmark = int(line.split('=')[1].strip().split()[0])
            elif line.startswith('IZONE='):
                izone_len += 1
                izone = int(line.split('=')[1].strip().split()[0])
            
            elif line.startswith('NDIME='):
                if izone_len > 1:
                    assert ndime is not None, "NDIME must be defined for zone"
                    assert nelem is not None, "NELEM must be defined for zone"
                    assert npoin is not None, "NPOIN must be defined for zone"
                    zone = Zone(izone-1, ndime, elements, element_types, np.array(points), markers, marker_types, nelem, npoin, nmark)
                    zones.append(zone)
                ndime = int(line.split('=')[1].strip().split()[0])
                nelem = None
                npoin = None
                elements = []
                element_types = []
                points = []
                markers = {}
                marker_types = {}
                element_index = None
                point_index = None
                marker_tag = None
                nmark_elems = None
                marker_index = None

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
                element_type = ElementType(int(line.split()[0]))
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
                marker_types[marker_tag].append(ElementType(int(marker_components[0])))

                if marker_index == nmark_elems - 1:
                    marker_index = None
                else:
                    marker_index += 1

        assert ndime is not None, "NDIME must be defined for zone"
        assert nelem is not None, "NELEM must be defined for zone"
        assert npoin is not None, "NPOIN must be defined for zone"
        zone = Zone(izone, ndime, elements, element_types, np.array(points), markers, marker_types, nelem, npoin, nmark)
        zones.append(zone)

        return Mesh(nzone, zones)

def combine_meshes(meshes: List[Mesh]):
    zones: List[Zone] = []
    izone = 1
    for mesh in meshes:
        for zone in mesh.zones:
            zone_copy = dataclasses.replace(zone)
            zone_copy.izone = izone
            zones.append(zone_copy)
            izone += 1
    return Mesh(nzone=len(zones), zones=zones)