from dataclasses import dataclass
from typing import Dict, List, Optional
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
    elements: List[npt.NDArray[np.uint16]]
    element_types: List[ElementType]
    points: npt.NDArray[np.float64]
    markers: Dict[str, List[npt.NDArray[np.uint16]]] = {}
    nelem: Optional[int] = None
    npoin: Optional[int] = None
    nmark: Optional[int] = None

    def __post_init__(self) -> None:
        if self.nelem is None:
            self.nelem = len(self.elements)
            self.npoin = len(self.points)
            self.nmark = len(self.markers)
        
            

@dataclass
class Mesh:
    nzone: int
    zones: List[Zone]
