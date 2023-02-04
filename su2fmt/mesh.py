from dataclasses import dataclass
from typing import Dict, List, Tuple
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
    marker_elements_to_tag: Dict[Tuple[int, int], str]

    @property
    def markers(self):
        marker_tag_to_elements: Dict[str, List[npt.NDArray[np.uint16]]] = {}
        for (elements, tag) in self.marker_elements_to_tag.items():
            if tag not in marker_tag_to_elements:
                marker_tag_to_elements[tag] = []
            marker_tag_to_elements[tag].append(np.array(elements))
        return [Marker(tag, len(elements), np.array(elements)) for (tag, elements) in marker_tag_to_elements.items()]


@dataclass
class Mesh:
    nzone: int
    zones: List[Zone]
