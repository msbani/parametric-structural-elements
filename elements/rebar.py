"""
elements/rebar.py
-----------------
Parametric Rebar / Reinforcement Bar element.

Can represent main longitudinal bars, stirrups, ties, or mesh reinforcement.
Parameters are expressed in metres unless stated otherwise.
"""

from __future__ import annotations
import math
from typing import Any, Dict, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import StructuralElement, Position


BAR_TYPES  = ("main", "stirrup", "tie", "mesh", "spiral", "cage")
ORIENTATIONS = ("longitudinal", "transverse", "diagonal", "horizontal", "vertical")


class Rebar(StructuralElement):
    """
    Parametric reinforcement bar / cage descriptor.

    Parameters
    ----------
    bar_type     : 'main' | 'stirrup' | 'tie' | 'mesh' | 'spiral' | 'cage'
    diameter     : bar diameter [m]  (e.g. 0.016 = Ø16 mm)
    length       : total bar/stirrup perimeter length [m]
    num_bars     : number of bars in the set
    spacing      : centre-to-centre spacing between bars [m]
    cover        : concrete cover [m]
    orientation  : 'longitudinal' | 'transverse' | 'diagonal' | 'horizontal' | 'vertical'
    hook_length  : hook extension length at ends [m]  (0 = no hook)
    lap_length   : splice / lap length [m]
    material     : key into MATERIALS catalogue (should be steel key)
    position     : Position(x, y, z) – start of the rebar / cage origin
    label        : human-readable tag
    """

    element_type = "Rebar"

    # Standard bar designations (nominal diameter in mm → area in mm²)
    BAR_AREAS: Dict[int, float] = {
        6: 28.3, 8: 50.3, 10: 78.5, 12: 113.1, 16: 201.1,
        20: 314.2, 25: 490.9, 32: 804.2, 40: 1256.6,
    }

    def __init__(
        self,
        bar_type: str = "main",
        diameter: float = 0.016,
        length: float = 3.0,
        num_bars: int = 4,
        spacing: float = 0.150,
        cover: float = 0.025,
        orientation: str = "longitudinal",
        hook_length: float = 0.0,
        lap_length: float = 0.0,
        material: str = "steel_fe500",
        position: Optional[Position] = None,
        label: str = "",
        element_id: Optional[str] = None,
    ):
        self.bar_type    = bar_type.lower()
        self.diameter    = diameter
        self.length      = length
        self.num_bars    = num_bars
        self.spacing     = spacing
        self.cover       = cover
        self.orientation = orientation.lower()
        self.hook_length = hook_length
        self.lap_length  = lap_length
        super().__init__(label=label, material=material,
                         position=position, element_id=element_id)

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if self.bar_type not in BAR_TYPES:
            raise ValueError(f"bar_type '{self.bar_type}' not recognised. Choose from {BAR_TYPES}.")
        if self.orientation not in ORIENTATIONS:
            raise ValueError(f"orientation '{self.orientation}' not recognised. Choose from {ORIENTATIONS}.")
        if self.diameter <= 0:
            raise ValueError("Bar diameter must be positive.")
        if self.length <= 0:
            raise ValueError("Bar length must be positive.")
        if self.num_bars < 1:
            raise ValueError("At least 1 bar required.")
        if self.spacing <= 0:
            raise ValueError("Bar spacing must be positive.")

    # ------------------------------------------------------------------
    def bar_area(self) -> float:
        """Cross-sectional area of a single bar [m²]."""
        return math.pi * (self.diameter / 2) ** 2

    def total_steel_area(self) -> float:
        """Total steel area of all bars in the set [m²]."""
        return self.num_bars * self.bar_area()

    def total_length(self) -> float:
        """Total bar length including hooks and lap [m]."""
        return self.length + 2 * self.hook_length + self.lap_length

    def unit_weight(self) -> float:
        """Unit weight of a single bar [kg] using steel density 7850 kg/m³."""
        return self.bar_area() * self.total_length() * 7850

    def total_weight(self) -> float:
        """Total weight of all bars [kg]."""
        return self.unit_weight() * self.num_bars

    def nearest_standard_dia(self) -> int:
        """Return the nearest standard bar designation (mm)."""
        dia_mm = self.diameter * 1000
        return min(self.BAR_AREAS.keys(), key=lambda d: abs(d - dia_mm))

    # ------------------------------------------------------------------
    def get_geometry(self) -> Dict[str, Any]:
        return {
            "type":       "rebar",
            "shape":      "cylinder",
            "origin":     self.position.as_tuple(),
            "dimensions": {
                "length": self.total_length(),
                "width":  self.diameter,
                "height": self.diameter,
            },
            "orientation": self.orientation,
            "color":       "#D4AF37",
        }

    # ------------------------------------------------------------------
    def summary(self) -> str:
        mat = self.material_info()
        lines = [
            f"{'─'*55}",
            f"  REBAR  |  {self.label}",
            f"{'─'*55}",
            f"  Bar type       : {self.bar_type.title()}",
            f"  Designation    : Ø{self.diameter*1000:.0f} mm  (nearest std: Ø{self.nearest_standard_dia()} mm)",
            f"  Number of bars : {self.num_bars}",
            f"  Bar length     : {self.length*1000:.0f} mm",
            f"  Hook length    : {self.hook_length*1000:.0f} mm (each end)",
            f"  Lap length     : {self.lap_length*1000:.0f} mm",
            f"  Total length   : {self.total_length()*1000:.0f} mm",
            f"  Spacing        : {self.spacing*1000:.0f} mm c/c",
            f"  Cover          : {self.cover*1000:.0f} mm",
            f"  Orientation    : {self.orientation.title()}",
            f"  Area (single)  : {self.bar_area()*1e6:.1f} mm²",
            f"  Area (total)   : {self.total_steel_area()*1e6:.1f} mm²",
            f"  Weight (total) : {self.total_weight():.2f} kg",
            f"  Material       : {mat.get('name', self.material)}",
            f"  Position (x,y,z): {self.position.x}, {self.position.y}, {self.position.z} m",
            f"{'─'*55}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _custom_fields(self) -> Dict[str, Any]:
        return {
            "bar_type":    self.bar_type,
            "diameter":    self.diameter,
            "length":      self.length,
            "num_bars":    self.num_bars,
            "spacing":     self.spacing,
            "cover":       self.cover,
            "orientation": self.orientation,
            "hook_length": self.hook_length,
            "lap_length":  self.lap_length,
        }
