"""Shared types and mappings for SU2 mesh format."""
from enum import Enum
from meshly import VTKCellType


class SU2ElementType(Enum):
    LINE = 3
    TRIANGLE = 5
    QUADRILATERAL = 9
    TETRAHEDRON = 10
    HEXAHEDRON = 12
    PRISM = 13
    PYRAMID = 14


# SU2 to VTK cell type mapping (single source of truth)
SU2_TO_VTK_MAPPING = {
    SU2ElementType.LINE.value: VTKCellType.VTK_LINE,
    SU2ElementType.TRIANGLE.value: VTKCellType.VTK_TRIANGLE,
    SU2ElementType.QUADRILATERAL.value: VTKCellType.VTK_QUAD,
    SU2ElementType.TETRAHEDRON.value: VTKCellType.VTK_TETRA,
    SU2ElementType.HEXAHEDRON.value: VTKCellType.VTK_HEXAHEDRON,
    SU2ElementType.PRISM.value: VTKCellType.VTK_WEDGE,
    SU2ElementType.PYRAMID.value: VTKCellType.VTK_PYRAMID,
}

# Reverse mapping derived from the forward mapping
VTK_TO_SU2_MAPPING = {v: k for k, v in SU2_TO_VTK_MAPPING.items()}
