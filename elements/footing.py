"""
elements/footing.py
-------------------
Parametric Footing element.

Supports isolated, combined, strip, and mat (raft) foundations.
Parameters are expressed in metres unless stated otherwise.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import StructuralElement, Position


FOOTING_TYPES = ("isolated", "combined", "strip", "mat", "pile_cap")


class Footing(StructuralElement):
    """
    Parametric reinforced-concrete footing / foundation.

    Parameters
    ----------
    footing_type  : 'isolated' | 'combined' | 'strip' | 'mat' | 'pile_cap'
    length        : plan length [m]
    width         : plan width [m]  (for strip/mat set to bay width)
    depth         : footing depth/thickness [m]
    pedestal_width : width of column pedestal above footing [m] (isolated/combined)
    pedestal_depth : depth of column pedestal [m] (isolated/combined)
    cover         : nominal cover [m]
    bar_diameter  : main bar diameter [m]
    bar_spacing   : bar spacing [m]
    bearing_capacity: allowable soil bearing capacity [kN/m²]
    material      : key into MATERIALS catalogue
    position      : Position(x, y, z) – bottom-centre of footing
    label         : human-readable tag
    """

    element_type = "Footing"

    def __init__(
        self,
        footing_type: str = "isolated",
        length: float = 2.0,
        width: float = 2.0,
        depth: float = 0.450,
        pedestal_width: float = 0.0,
        pedestal_depth: float = 0.0,
        cover: float = 0.050,
        bar_diameter: float = 0.016,
        bar_spacing: float = 0.200,
        bearing_capacity: float = 150.0,
        material: str = "concrete_m25",
        position: Optional[Position] = None,
        label: str = "",
        element_id: Optional[str] = None,
    ):
        self.footing_type    = footing_type.lower()
        self.length          = length
        self.width           = width
        self.depth           = depth
        self.pedestal_width  = pedestal_width
        self.pedestal_depth  = pedestal_depth
        self.cover           = cover
        self.bar_diameter    = bar_diameter
        self.bar_spacing     = bar_spacing
        self.bearing_capacity = bearing_capacity
        super().__init__(label=label, material=material,
                         position=position, element_id=element_id)

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if self.footing_type not in FOOTING_TYPES:
            raise ValueError(
                f"footing_type '{self.footing_type}' not recognised. "
                f"Choose from {FOOTING_TYPES}."
            )
        if self.length <= 0 or self.width <= 0 or self.depth <= 0:
            raise ValueError("Footing length, width, and depth must be positive.")
        if self.cover >= self.depth / 2:
            raise ValueError("Cover exceeds half the footing depth.")
        if self.bearing_capacity <= 0:
            raise ValueError("Bearing capacity must be positive.")

    # ------------------------------------------------------------------
    def plan_area(self) -> float:
        """Plan area [m²]."""
        return self.length * self.width

    def volume(self) -> float:
        """Concrete volume [m³]."""
        return self.plan_area() * self.depth

    def effective_depth(self) -> float:
        """Effective depth [m]."""
        return self.depth - self.cover - self.bar_diameter / 2

    def safe_load_capacity(self) -> float:
        """Approximate safe axial load [kN] (gross bearing × plan area)."""
        return self.bearing_capacity * self.plan_area()

    # ------------------------------------------------------------------
    def get_geometry(self) -> Dict[str, Any]:
        return {
            "type":       "footing",
            "shape":      "rectangular",
            "origin":     self.position.as_tuple(),
            "dimensions": {
                "length": self.length,
                "width":  self.width,
                "height": self.depth,
            },
            "color":      "#A0785A",
        }

    # ------------------------------------------------------------------
    def summary(self) -> str:
        mat = self.material_info()
        lines = [
            f"{'─'*55}",
            f"  FOOTING  |  {self.label}",
            f"{'─'*55}",
            f"  Type           : {self.footing_type.replace('_',' ').title()}",
            f"  L × W × D      : {self.length*1000:.0f} × {self.width*1000:.0f} × {self.depth*1000:.0f} mm",
            f"  Cover          : {self.cover*1000:.0f} mm",
            f"  Effective Depth: {self.effective_depth()*1000:.1f} mm",
            f"  Rebar          : Ø{self.bar_diameter*1000:.0f} mm @ {self.bar_spacing*1000:.0f} mm c/c (both ways)",
            f"  Bearing Cap.   : {self.bearing_capacity:.0f} kN/m²",
            f"  Safe Load Cap. : {self.safe_load_capacity():.1f} kN",
            f"  Material       : {mat.get('name', self.material)}",
            f"  Position (x,y,z): {self.position.x}, {self.position.y}, {self.position.z} m",
            f"  Plan Area      : {self.plan_area():.2f} m²",
            f"  Volume (conc.) : {self.volume():.4f} m³",
            f"{'─'*55}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _custom_fields(self) -> Dict[str, Any]:
        return {
            "footing_type":    self.footing_type,
            "length":          self.length,
            "width":           self.width,
            "depth":           self.depth,
            "pedestal_width":  self.pedestal_width,
            "pedestal_depth":  self.pedestal_depth,
            "cover":           self.cover,
            "bar_diameter":    self.bar_diameter,
            "bar_spacing":     self.bar_spacing,
            "bearing_capacity":self.bearing_capacity,
        }
