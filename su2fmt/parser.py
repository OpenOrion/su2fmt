from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import numpy.typing as npt
from enum import Enum 

class ElementType(Enum):
    LINE = 3
    TRIANGLE = 5
    QUADRILATERAL = 9
    TETRAHEDRAL = 10
    HEXAHEDRAL = 12
    PRISM = 13
    PYRAMID = 14

@dataclass
class Marker:
    tag: str
    nelem: int
    elements: npt.NDArray[np.uint16]


@dataclass
class Zone:
    izone: int
    ndime: int
    nelem: int
    npoin: int
    nmark: int
    elements: List[npt.NDArray[np.uint16]]
    element_types: List[ElementType]
    points: npt.NDArray[np.float32]
    markers: Dict[Tuple[int, int], str]

@dataclass
class Mesh:
    nzone: int
    zones: List[Zone]

    @staticmethod
    def from_file(file_path: str):
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
            markers: Dict[Tuple[int, int], str] = {}
            
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
                        zone = Zone(izone-1, ndime, nelem, npoin, nmark, elements, element_types, np.array(points), markers)
                        zones.append(zone)
                    ndime = int(line.split('=')[1])
                    nelem = None
                    npoin = None
                    elements = []
                    element_types = []
                    points = []
                    markers = {}
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
                    markers[(marker_elements[0], marker_elements[1])] = marker_tag
                    if marker_index == nmark_elems - 1:
                        marker_index = None
                    else:
                        marker_index += 1

            assert ndime is not None, "NDIME must be defined for zone"
            assert nelem is not None, "NELEM must be defined for zone"
            assert npoin is not None, "NPOIN must be defined for zone"
            zone = Zone(izone, ndime, nelem, npoin, nmark, elements, element_types, np.array(points), markers)
            zones.append(zone)

            return Mesh(nzone, zones)

