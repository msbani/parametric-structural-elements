"""
structural_element.py
---------------------
Abstract base class for all parametric structural elements.
Provides common properties, validation contract, serialization helpers,
and a human-readable summary interface.
"""

from __future__ import annotations
import abc
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, Tuple


# ---------------------------------------------------------------------------
# Material catalogue
# ---------------------------------------------------------------------------

MATERIALS = {
    "concrete_m20":   {"name": "Concrete M20",   "fc_MPa": 20,  "density_kg_m3": 2400, "type": "concrete"},
    "concrete_m25":   {"name": "Concrete M25",   "fc_MPa": 25,  "density_kg_m3": 2400, "type": "concrete"},
    "concrete_m30":   {"name": "Concrete M30",   "fc_MPa": 30,  "density_kg_m3": 2400, "type": "concrete"},
    "concrete_m40":   {"name": "Concrete M40",   "fc_MPa": 40,  "density_kg_m3": 2500, "type": "concrete"},
    "steel_fe415":    {"name": "Steel Fe415",    "fy_MPa": 415, "density_kg_m3": 7850, "type": "steel"},
    "steel_fe500":    {"name": "Steel Fe500",    "fy_MPa": 500, "density_kg_m3": 7850, "type": "steel"},
    "timber_douglas":  {"name": "Douglas Fir",   "fb_MPa": 12,  "density_kg_m3": 530,  "type": "timber"},
    "steel_astm_a36": {"name": "ASTM A36 Steel", "fy_MPa": 250, "density_kg_m3": 7850, "type": "steel"},
    "steel_astm_a992":{"name": "ASTM A992 Steel","fy_MPa": 345, "density_kg_m3": 7850, "type": "steel"},
}


# ---------------------------------------------------------------------------
# Common position type
# ---------------------------------------------------------------------------

@dataclass
class Position:
    """3-D Cartesian position in metres."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __repr__(self) -> str:             # pragma: no cover
        return f"Position(x={self.x}, y={self.y}, z={self.z})"

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


# ---------------------------------------------------------------------------
# Abstract base class
# ---------------------------------------------------------------------------

class StructuralElement(abc.ABC):
    """
    Abstract base for every parametric structural element.

    Subclasses must implement:
        validate()    – raise ValueError for illegal parameter combinations
        get_geometry()– return a dict describing bounding geometry (for viz)
        summary()     – return a formatted multi-line string description
        element_type  – class-level string constant (e.g. "Column")
    """

    element_type: str = "Generic"

    def __init__(
        self,
        label: str = "",
        material: str = "concrete_m25",
        position: Optional[Position] = None,
        element_id: Optional[str] = None,
    ):
        self.element_id: str = element_id or str(uuid.uuid4())[:8]
        self.label: str = label or f"{self.element_type}-{self.element_id}"
        self.material: str = material
        self.position: Position = position or Position()
        self.validate()

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def validate(self) -> None:
        """Raise ValueError when parameters are physically invalid."""

    @abc.abstractmethod
    def get_geometry(self) -> Dict[str, Any]:
        """
        Return a dict that the visualiser can consume.
        Minimum keys: 'type', 'origin', 'dimensions'.
        """

    @abc.abstractmethod
    def summary(self) -> str:
        """Return a human-readable multi-line summary of this element."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def material_info(self) -> Dict[str, Any]:
        """Look up material properties from the catalogue."""
        return MATERIALS.get(self.material, {"name": self.material})

    def to_dict(self) -> Dict[str, Any]:
        """Serialise element to a plain dictionary (JSON-ready)."""
        base = {
            "element_type": self.element_type,
            "element_id":   self.element_id,
            "label":        self.label,
            "material":     self.material,
            "position":     asdict(self.position),
        }
        base.update(self._custom_fields())
        return base

    def _custom_fields(self) -> Dict[str, Any]:
        """Override in subclasses to add element-specific fields to to_dict."""
        return {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuralElement":
        """
        Reconstruct an element from a dictionary produced by to_dict().
        Each subclass should override if it needs custom parsing.
        """
        pos_data = data.pop("position", {})
        data.pop("element_type", None)
        position = Position(**pos_data)
        return cls(position=position, **data)

    def __repr__(self) -> str:             # pragma: no cover
        return f"<{self.element_type} label='{self.label}' @ {self.position}>"

    # ------------------------------------------------------------------
    # Volume helper (override in subclass for non-prism shapes)
    # ------------------------------------------------------------------

    def volume(self) -> Optional[float]:
        """Return approximate volume in m³ if calculable, else None."""
        geom = self.get_geometry()
        dims = geom.get("dimensions", {})
        try:
            return dims["length"] * dims["width"] * dims["height"]
        except (KeyError, TypeError):
            return None
