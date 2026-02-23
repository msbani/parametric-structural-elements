"""
elements/column.py
------------------
Parametric Column element.

Supports rectangular and circular cross-sections.
Parameters are expressed in metres unless stated otherwise.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import StructuralElement, Position


class Column(StructuralElement):
    """
    Parametric reinforced-concrete or steel column.

    Parameters
    ----------
    shape        : 'rectangular' | 'circular'
    width        : section width  [m]  – rectangular only
    depth        : section depth  [m]  – rectangular only
    diameter     : section diameter [m] – circular only
    height       : column height [m]
    cover        : clear concrete cover to rebar [m]  (default 0.04 m = 40 mm)
    num_bars     : number of longitudinal bars
    bar_diameter : diameter of longitudinal bars [m]  (default 0.016 m = 16 mm)
    tie_spacing  : spacing of lateral ties / links [m]
    material     : key into MATERIALS catalogue
    position     : Position(x, y, z) – base-centre of column
    label        : human-readable tag
    """

    element_type = "Column"

    def __init__(
        self,
        shape: str = "rectangular",
        width: float = 0.45,
        depth: float = 0.45,
        diameter: float = 0.50,
        height: float = 3.0,
        cover: float = 0.040,
        num_bars: int = 8,
        bar_diameter: float = 0.016,
        tie_spacing: float = 0.150,
        material: str = "concrete_m25",
        position: Optional[Position] = None,
        label: str = "",
        element_id: Optional[str] = None,
    ):
        self.shape        = shape.lower()
        self.width        = width
        self.depth        = depth
        self.diameter     = diameter
        self.height       = height
        self.cover        = cover
        self.num_bars     = num_bars
        self.bar_diameter = bar_diameter
        self.tie_spacing  = tie_spacing
        super().__init__(label=label, material=material,
                         position=position, element_id=element_id)

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if self.shape not in ("rectangular", "circular"):
            raise ValueError(f"Column shape must be 'rectangular' or 'circular', got '{self.shape}'.")
        if self.shape == "rectangular":
            if self.width <= 0 or self.depth <= 0:
                raise ValueError("Column width and depth must be positive.")
            if self.cover >= min(self.width, self.depth) / 2:
                raise ValueError("Cover is too large relative to section dimensions.")
        else:
            if self.diameter <= 0:
                raise ValueError("Column diameter must be positive.")
            if self.cover >= self.diameter / 2:
                raise ValueError("Cover is too large relative to diameter.")
        if self.height <= 0:
            raise ValueError("Column height must be positive.")
        if self.num_bars < 4:
            raise ValueError("Minimum 4 longitudinal bars required in a column.")
        if self.tie_spacing <= 0:
            raise ValueError("Tie spacing must be positive.")

    # ------------------------------------------------------------------
    def cross_section_area(self) -> float:
        """Gross cross-section area [m²]."""
        if self.shape == "rectangular":
            return self.width * self.depth
        return math.pi * (self.diameter / 2) ** 2

    def steel_area(self) -> float:
        """Total longitudinal steel area [m²]."""
        return self.num_bars * math.pi * (self.bar_diameter / 2) ** 2

    def steel_ratio(self) -> float:
        """Longitudinal steel ratio (ρ = As / Ag)."""
        return self.steel_area() / self.cross_section_area()

    def volume(self) -> float:
        """Concrete volume [m³]."""
        return self.cross_section_area() * self.height

    # ------------------------------------------------------------------
    def get_geometry(self) -> Dict[str, Any]:
        if self.shape == "rectangular":
            dims = {"length": self.depth, "width": self.width, "height": self.height}
        else:
            dims = {"length": self.diameter, "width": self.diameter, "height": self.height}
        return {
            "type":       "column",
            "shape":      self.shape,
            "origin":     self.position.as_tuple(),
            "dimensions": dims,
            "color":      "#4A90D9",
        }

    # ------------------------------------------------------------------
    def summary(self) -> str:
        mat = self.material_info()
        lines = [
            f"{'─'*55}",
            f"  COLUMN  |  {self.label}",
            f"{'─'*55}",
            f"  Shape         : {self.shape.capitalize()}",
        ]
        if self.shape == "rectangular":
            lines += [
                f"  Width × Depth  : {self.width*1000:.0f} mm × {self.depth*1000:.0f} mm",
            ]
        else:
            lines += [
                f"  Diameter       : {self.diameter*1000:.0f} mm",
            ]
        lines += [
            f"  Height         : {self.height*1000:.0f} mm",
            f"  Cover          : {self.cover*1000:.0f} mm",
            f"  Long. Bars     : {self.num_bars} × Ø{self.bar_diameter*1000:.0f} mm",
            f"  Steel Ratio    : {self.steel_ratio()*100:.2f} %",
            f"  Tie Spacing    : {self.tie_spacing*1000:.0f} mm",
            f"  Material       : {mat.get('name', self.material)}",
            f"  Position (x,y,z): {self.position.x}, {self.position.y}, {self.position.z} m",
            f"  Gross Area     : {self.cross_section_area()*1e6:.0f} mm²",
            f"  Volume (conc.) : {self.volume():.4f} m³",
            f"{'─'*55}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _custom_fields(self) -> Dict[str, Any]:
        return {
            "shape":        self.shape,
            "width":        self.width,
            "depth":        self.depth,
            "diameter":     self.diameter,
            "height":       self.height,
            "cover":        self.cover,
            "num_bars":     self.num_bars,
            "bar_diameter": self.bar_diameter,
            "tie_spacing":  self.tie_spacing,
        }
