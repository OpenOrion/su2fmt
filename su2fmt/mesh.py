from dataclasses import dataclass
from typing import Sequence, Optional
import numpy as np
import numpy.typing as npt
from enum import Enum
import dataclasses

class ElementType(Enum):
    LINE = 3
    TRIANGLE = 5
    QUADRILATERAL = 9
    TETRAHEDRON = 10
    HEXAHEDRON = 12
    PRISM = 13
    PYRAMID = 14

@dataclass
class Zone:
    izone: int
    ndime: int
    elements: Sequence[npt.NDArray[np.int64]]
    element_types: Sequence[ElementType]
    points: npt.NDArray[np.float32]
    markers: dict[str, Sequence[npt.NDArray[np.int64]]] = dataclasses.field(default_factory=dict)
    marker_types: dict[str,Sequence[ElementType]] = dataclasses.field(default_factory=dict)
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
    zones: Sequence[Zone]
