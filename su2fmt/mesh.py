from typing import Optional, Dict
import numpy as np
from enum import Enum
from meshly import Mesh
from pydantic import Field

class ElementType(Enum):
    LINE = 3
    TRIANGLE = 5
    QUADRILATERAL = 9
    TETRAHEDRON = 10
    HEXAHEDRON = 12
    PRISM = 13
    PYRAMID = 14

class SU2Mesh(Mesh):
    """
    A mesh class for SU2 format files, inheriting from meshly.Mesh.
    
    This extends the base Mesh class with SU2-specific attributes like
    element types, markers, and zone information.
    """
    # SU2-specific attributes
    element_types: np.ndarray = Field(..., description="Element types for each element")
    markers: Dict[str, np.ndarray] = Field(default_factory=dict, description="Boundary markers")
    marker_types: Dict[str, np.ndarray] = Field(default_factory=dict, description="Marker element types")
    
    # Zone information
    izone: int = Field(1, description="Zone index")
    ndime: int = Field(3, description="Number of dimensions from file")
    
    @property
    def nelem(self) -> int:
        """Number of elements (derived from element_types)."""
        return len(self.element_types) if len(self.element_types) > 0 else 0
    
    @property
    def npoin(self) -> int:
        """Number of points (derived from vertices)."""
        return len(self.vertices) if len(self.vertices) > 0 else 0
    
    @property
    def nmark(self) -> int:
        """Number of markers (derived from markers dict)."""
        return len(self.markers)
