"""
elements/beam.py
----------------
Parametric Beam element.

Parameters are expressed in metres unless stated otherwise.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import StructuralElement, Position


class Beam(StructuralElement):
    """
    Parametric reinforced-concrete beam.

    Parameters
    ----------
    width        : section width (bw) [m]
    depth        : overall section depth (D) [m]
    length       : clear/effective span [m]
    span_type    : 'simply_supported' | 'continuous' | 'cantilever'
    cover        : nominal cover [m]
    top_bars     : number of top (compression) longitudinal bars
    bottom_bars  : number of bottom (tension) longitudinal bars
    bar_diameter : diameter of longitudinal bars [m]
    stirrup_dia  : diameter of stirrups/links [m]
    stirrup_spacing : centre-to-centre stirrup spacing [m]
    orientation  : 'x' | 'y'  – which horizontal axis the beam runs along
    material     : key into MATERIALS catalogue
    start_position: Position(x, y, z) of the start end (centroid of section)
    label        : human-readable tag
    """

    element_type = "Beam"

    def __init__(
        self,
        width: float = 0.30,
        depth: float = 0.60,
        length: float = 5.0,
        span_type: str = "simply_supported",
        cover: float = 0.025,
        top_bars: int = 2,
        bottom_bars: int = 3,
        bar_diameter: float = 0.020,
        stirrup_dia: float = 0.010,
        stirrup_spacing: float = 0.150,
        orientation: str = "x",
        material: str = "concrete_m25",
        start_position: Optional[Position] = None,
        label: str = "",
        element_id: Optional[str] = None,
    ):
        self.width           = width
        self.depth           = depth
        self.length          = length
        self.span_type       = span_type.lower()
        self.cover           = cover
        self.top_bars        = top_bars
        self.bottom_bars     = bottom_bars
        self.bar_diameter    = bar_diameter
        self.stirrup_dia     = stirrup_dia
        self.stirrup_spacing = stirrup_spacing
        self.orientation     = orientation.lower()
        super().__init__(label=label, material=material,
                         position=start_position, element_id=element_id)

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if self.width <= 0 or self.depth <= 0 or self.length <= 0:
            raise ValueError("Beam width, depth, and length must all be positive.")
        if self.span_type not in ("simply_supported", "continuous", "cantilever"):
            raise ValueError(f"Invalid span_type '{self.span_type}'.")
        if self.orientation not in ("x", "y"):
            raise ValueError("Orientation must be 'x' or 'y'.")
        if self.cover >= self.width / 2 or self.cover >= self.depth / 2:
            raise ValueError("Cover cannot exceed half the section dimension.")
        if self.stirrup_spacing <= 0:
            raise ValueError("Stirrup spacing must be positive.")

    # ------------------------------------------------------------------
    def effective_depth(self) -> float:
        """Effective depth d = D - cover - Ø_stirrup - Ø_bar/2 [m]."""
        return self.depth - self.cover - self.stirrup_dia - self.bar_diameter / 2

    def cross_section_area(self) -> float:
        """Gross section area [m²]."""
        return self.width * self.depth

    def steel_area_tension(self) -> float:
        """Tension steel area [m²]."""
        return self.bottom_bars * math.pi * (self.bar_diameter / 2) ** 2

    def steel_ratio(self) -> float:
        """Flexural tension steel ratio (ρ = As / b·d)."""
        return self.steel_area_tension() / (self.width * self.effective_depth())

    def volume(self) -> float:
        """Concrete volume [m³]."""
        return self.cross_section_area() * self.length

    def num_stirrups(self) -> int:
        """Approximate number of stirrups over the span."""
        return max(1, int(self.length / self.stirrup_spacing) + 1)

    # ------------------------------------------------------------------
    def get_geometry(self) -> Dict[str, Any]:
        if self.orientation == "x":
            dims = {"length": self.length, "width": self.width, "height": self.depth}
        else:
            dims = {"length": self.width, "width": self.length, "height": self.depth}
        return {
            "type":        "beam",
            "shape":       "rectangular",
            "origin":      self.position.as_tuple(),
            "dimensions":  dims,
            "orientation": self.orientation,
            "color":       "#E07B39",
        }

    # ------------------------------------------------------------------
    def summary(self) -> str:
        mat = self.material_info()
        lines = [
            f"{'─'*55}",
            f"  BEAM  |  {self.label}",
            f"{'─'*55}",
            f"  Width × Depth  : {self.width*1000:.0f} mm × {self.depth*1000:.0f} mm",
            f"  Length (span)  : {self.length*1000:.0f} mm",
            f"  Span type      : {self.span_type.replace('_',' ').title()}",
            f"  Effective depth: {self.effective_depth()*1000:.1f} mm",
            f"  Cover          : {self.cover*1000:.0f} mm",
            f"  Top bars       : {self.top_bars} × Ø{self.bar_diameter*1000:.0f} mm",
            f"  Bottom bars    : {self.bottom_bars} × Ø{self.bar_diameter*1000:.0f} mm",
            f"  Steel ratio    : {self.steel_ratio()*100:.3f} %",
            f"  Stirrups       : Ø{self.stirrup_dia*1000:.0f} @ {self.stirrup_spacing*1000:.0f} mm  (~{self.num_stirrups()} nos.)",
            f"  Orientation    : along {self.orientation.upper()}-axis",
            f"  Material       : {mat.get('name', self.material)}",
            f"  Position (x,y,z): {self.position.x}, {self.position.y}, {self.position.z} m",
            f"  Volume (conc.) : {self.volume():.4f} m³",
            f"{'─'*55}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _custom_fields(self) -> Dict[str, Any]:
        return {
            "width":            self.width,
            "depth":            self.depth,
            "length":           self.length,
            "span_type":        self.span_type,
            "cover":            self.cover,
            "top_bars":         self.top_bars,
            "bottom_bars":      self.bottom_bars,
            "bar_diameter":     self.bar_diameter,
            "stirrup_dia":      self.stirrup_dia,
            "stirrup_spacing":  self.stirrup_spacing,
            "orientation":      self.orientation,
        }
