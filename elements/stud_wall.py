"""
elements/stud_wall.py
---------------------
Parametric Stud Wall element.

Covers light-gauge steel stud walls and timber stud walls used in
residential, data-centre, and commercial construction.
Parameters are expressed in metres unless stated otherwise.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import StructuralElement, Position


STUD_MATERIALS = ("timber", "light_gauge_steel", "cold_formed_steel")
WALL_TYPES     = ("load_bearing", "non_load_bearing", "shear", "partition", "fire_rated")


class StudWall(StructuralElement):
    """
    Parametric stud wall (timber or light-gauge steel).

    Parameters
    ----------
    length            : total wall length [m]
    height            : wall height / stud length [m]
    stud_spacing      : centre-to-centre stud spacing [m]  (typical: 0.40 or 0.60 m)
    stud_width        : width of stud section [m]           (e.g. 0.038 for 38 mm)
    stud_depth        : depth of stud section [m]           (e.g. 0.089 for 89 mm)
    sheathing_thick   : thickness of one board/sheet of sheathing [m]
    num_sheathing_layers: number of sheathing layers (each side)
    bottom_plate_thick: thickness of bottom/top plate [m]
    wall_type         : 'load_bearing' | 'non_load_bearing' | 'shear' | 'partition' | 'fire_rated'
    stud_material     : 'timber' | 'light_gauge_steel' | 'cold_formed_steel'
    material          : key into MATERIALS catalogue (overall wall material for cost)
    orientation       : wall face normal direction 'x' | 'y'
    position          : Position(x, y, z) – corner of wall at base
    label             : human-readable tag
    """

    element_type = "StudWall"

    def __init__(
        self,
        length: float = 4.0,
        height: float = 3.0,
        stud_spacing: float = 0.400,
        stud_width: float = 0.038,
        stud_depth: float = 0.089,
        sheathing_thick: float = 0.0125,
        num_sheathing_layers: int = 1,
        bottom_plate_thick: float = 0.038,
        wall_type: str = "load_bearing",
        stud_material: str = "timber",
        material: str = "timber_douglas",
        orientation: str = "x",
        position: Optional[Position] = None,
        label: str = "",
        element_id: Optional[str] = None,
    ):
        self.length               = length
        self.height               = height
        self.stud_spacing         = stud_spacing
        self.stud_width           = stud_width
        self.stud_depth           = stud_depth
        self.sheathing_thick      = sheathing_thick
        self.num_sheathing_layers = num_sheathing_layers
        self.bottom_plate_thick   = bottom_plate_thick
        self.wall_type            = wall_type.lower()
        self.stud_material        = stud_material.lower()
        self.orientation          = orientation.lower()
        super().__init__(label=label, material=material,
                         position=position, element_id=element_id)

    # ------------------------------------------------------------------
    def validate(self) -> None:
        if self.length <= 0 or self.height <= 0:
            raise ValueError("StudWall length and height must be positive.")
        if self.stud_spacing <= 0:
            raise ValueError("Stud spacing must be positive.")
        if self.wall_type not in WALL_TYPES:
            raise ValueError(
                f"wall_type '{self.wall_type}' not recognised. Choose from {WALL_TYPES}."
            )
        if self.stud_material not in STUD_MATERIALS:
            raise ValueError(
                f"stud_material '{self.stud_material}' not recognised. Choose from {STUD_MATERIALS}."
            )
        if self.orientation not in ("x", "y"):
            raise ValueError("Orientation must be 'x' or 'y'.")

    # ------------------------------------------------------------------
    def total_thickness(self) -> float:
        """Overall wall thickness including studs and sheathing [m]."""
        return self.stud_depth + 2 * self.num_sheathing_layers * self.sheathing_thick

    def num_studs(self) -> int:
        """Approximate number of studs in the wall."""
        return max(2, int(self.length / self.stud_spacing) + 1)

    def stud_height(self) -> float:
        """Net stud length (height minus top & bottom plates) [m]."""
        return self.height - 2 * self.bottom_plate_thick

    def face_area(self) -> float:
        """Face (elevation) area of the wall [m²]."""
        return self.length * self.height

    def volume(self) -> float:
        """Overall wall volume (bounding box) [m³]."""
        return self.face_area() * self.total_thickness()

    def stud_volume(self) -> float:
        """Total timber/steel volume in studs [m³]."""
        return (self.stud_width * self.stud_depth * self.stud_height()) * self.num_studs()

    # ------------------------------------------------------------------
    def get_geometry(self) -> Dict[str, Any]:
        if self.orientation == "x":
            dims = {"length": self.length, "width": self.total_thickness(), "height": self.height}
        else:
            dims = {"length": self.total_thickness(), "width": self.length, "height": self.height}
        return {
            "type":       "stud_wall",
            "shape":      "rectangular",
            "origin":     self.position.as_tuple(),
            "dimensions": dims,
            "color":      "#C8A97E",
        }

    # ------------------------------------------------------------------
    def summary(self) -> str:
        mat = self.material_info()
        lines = [
            f"{'─'*55}",
            f"  STUD WALL  |  {self.label}",
            f"{'─'*55}",
            f"  Wall Type      : {self.wall_type.replace('_',' ').title()}",
            f"  Stud Material  : {self.stud_material.replace('_',' ').title()}",
            f"  Length × Height: {self.length*1000:.0f} mm × {self.height*1000:.0f} mm",
            f"  Stud Section   : {self.stud_width*1000:.0f} × {self.stud_depth*1000:.0f} mm",
            f"  Stud Spacing   : {self.stud_spacing*1000:.0f} mm c/c",
            f"  Number of Studs: {self.num_studs()}",
            f"  Stud Height    : {self.stud_height()*1000:.0f} mm (net, btw plates)",
            f"  Sheathing      : {self.num_sheathing_layers} layer(s) × {self.sheathing_thick*1000:.1f} mm (per side)",
            f"  Total Thickness: {self.total_thickness()*1000:.1f} mm",
            f"  Orientation    : normal to {self.orientation.upper()}-axis",
            f"  Material       : {mat.get('name', self.material)}",
            f"  Position (x,y,z): {self.position.x}, {self.position.y}, {self.position.z} m",
            f"  Face Area      : {self.face_area():.2f} m²",
            f"  Stud Volume    : {self.stud_volume():.4f} m³",
            f"{'─'*55}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _custom_fields(self) -> Dict[str, Any]:
        return {
            "length":                self.length,
            "height":                self.height,
            "stud_spacing":          self.stud_spacing,
            "stud_width":            self.stud_width,
            "stud_depth":            self.stud_depth,
            "sheathing_thick":       self.sheathing_thick,
            "num_sheathing_layers":  self.num_sheathing_layers,
            "bottom_plate_thick":    self.bottom_plate_thick,
            "wall_type":             self.wall_type,
            "stud_material":         self.stud_material,
            "orientation":           self.orientation,
        }
