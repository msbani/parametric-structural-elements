"""
elements/slab.py
----------------
Parametric Slab element.

Parameters are expressed in metres unless stated otherwise.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import StructuralElement, Position


SLAB_TYPES = ("one_way", "two_way", "flat_plate", "flat_slab", "waffle", "ribbed")


class Slab(StructuralElement):
    """
    Parametric reinforced-concrete slab.

    Parameters
    ----------
    length        : longer plan dimension [m]
    width         : shorter plan dimension [m]
    thickness     : overall slab thickness [m]
    slab_type     : 'one_way' | 'two_way' | 'flat_plate' | 'flat_slab' | 'waffle' | 'ribbed'
    cover         : nominal cover to rebar [m]
    bar_diameter  : main reinforcement bar diameter [m]
    bar_spacing   : centre-to-centre bar spacing [m]
    material      : key into MATERIALS catalogue
    position      : Position(x, y, z) – corner origin of the slab (bottom face)
    label         : human-readable tag
    """

    element_type = "Slab"

    def __init__(
        self,
        length: float = 6.0,
        width: float = 5.0,
        thickness: float = 0.150,
        slab_type: str = "two_way",
        cover: float = 0.020,
        bar_diameter: float = 0.012,
        bar_spacing: float = 0.150,
        material: str = "concrete_m25",
        position: Optional[Position] = None,
        label: str = "",
        element_id: Optional[str] = None,
    ):
        self.length       = length
        self.width        = width
        self.thickness    = thickness
        self.slab_type    = slab_type.lower()
        self.cover        = cover
        self.bar_diameter = bar_diameter
        self.bar_spacing  = bar_spacing
        super().__init__(label=label, material=material,
                         position=position, element_id=element_id)

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if self.length <= 0 or self.width <= 0:
            raise ValueError("Slab length and width must be positive.")
        if self.thickness <= 0:
            raise ValueError("Slab thickness must be positive.")
        if self.slab_type not in SLAB_TYPES:
            raise ValueError(
                f"slab_type '{self.slab_type}' not recognised. "
                f"Choose from {SLAB_TYPES}."
            )
        if self.cover >= self.thickness / 2:
            raise ValueError("Cover cannot exceed half the slab thickness.")
        if self.bar_spacing <= 0:
            raise ValueError("Bar spacing must be positive.")

    # ------------------------------------------------------------------
    def effective_depth(self) -> float:
        """Effective depth [m]."""
        return self.thickness - self.cover - self.bar_diameter / 2

    def plan_area(self) -> float:
        """Plan (surface) area [m²]."""
        return self.length * self.width

    def volume(self) -> float:
        """Concrete volume [m³]."""
        return self.plan_area() * self.thickness

    def bars_per_width(self) -> int:
        """Approx. number of bars per metre width."""
        return max(1, int(1.0 / self.bar_spacing))

    def span_ratio(self) -> float:
        """Ly / Lx ratio (useful for one- vs two-way slab classification)."""
        return max(self.length, self.width) / min(self.length, self.width)

    # ------------------------------------------------------------------
    def get_geometry(self) -> Dict[str, Any]:
        return {
            "type":       "slab",
            "shape":      "rectangular",
            "origin":     self.position.as_tuple(),
            "dimensions": {
                "length": self.length,
                "width":  self.width,
                "height": self.thickness,
            },
            "color":      "#7BC8A4",
        }

    # ------------------------------------------------------------------
    def summary(self) -> str:
        mat = self.material_info()
        lines = [
            f"{'─'*55}",
            f"  SLAB  |  {self.label}",
            f"{'─'*55}",
            f"  Type           : {self.slab_type.replace('_',' ').title()}",
            f"  Length × Width : {self.length*1000:.0f} mm × {self.width*1000:.0f} mm",
            f"  Thickness      : {self.thickness*1000:.0f} mm",
            f"  Span ratio     : {self.span_ratio():.2f} (Ly/Lx)",
            f"  Cover          : {self.cover*1000:.0f} mm",
            f"  Effective Depth: {self.effective_depth()*1000:.1f} mm",
            f"  Rebar          : Ø{self.bar_diameter*1000:.0f} mm @ {self.bar_spacing*1000:.0f} mm c/c",
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
            "length":       self.length,
            "width":        self.width,
            "thickness":    self.thickness,
            "slab_type":    self.slab_type,
            "cover":        self.cover,
            "bar_diameter": self.bar_diameter,
            "bar_spacing":  self.bar_spacing,
        }
