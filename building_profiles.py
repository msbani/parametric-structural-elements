"""
building_profiles.py
--------------------
Pre-defined parametric profiles for common building types.

Each profile contains sensible default parameter overrides for
every structural element type. A BIM/structural engineer can
use apply_profile() to quickly stamp defaults onto any element,
then fine-tune individual parameters as needed.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from structural_element import StructuralElement


# ---------------------------------------------------------------------------
# Profile dataclass
# ---------------------------------------------------------------------------

@dataclass
class BuildingProfile:
    """
    Container of default parameters per building type for each element class.

    Each *_defaults dict holds keyword arguments matching the constructor
    signature of the corresponding element class (minus position/label/id).
    """
    name: str
    description: str

    column_defaults:    Dict[str, Any] = field(default_factory=dict)
    beam_defaults:      Dict[str, Any] = field(default_factory=dict)
    slab_defaults:      Dict[str, Any] = field(default_factory=dict)
    footing_defaults:   Dict[str, Any] = field(default_factory=dict)
    rebar_defaults:     Dict[str, Any] = field(default_factory=dict)
    stud_wall_defaults: Dict[str, Any] = field(default_factory=dict)

    # Class-level registry (shared across all instances)
    _registry: ClassVar[Dict[str, "BuildingProfile"]] = {}

    def __post_init__(self):
        BuildingProfile._registry[self.name] = self

    @classmethod
    def get(cls, name: str) -> "BuildingProfile":
        """Retrieve a registered profile by name (case-insensitive)."""
        key = name.lower().replace(" ", "_")
        for k, v in cls._registry.items():
            if k.lower().replace(" ", "_") == key:
                return v
        raise KeyError(
            f"No building profile named '{name}'. "
            f"Available: {list(cls._registry.keys())}"
        )

    @classmethod
    def list_profiles(cls) -> list:
        """Return names of all registered profiles."""
        return list(cls._registry.keys())


# ---------------------------------------------------------------------------
# Utility function
# ---------------------------------------------------------------------------

def apply_profile(element: "StructuralElement", profile: BuildingProfile) -> "StructuralElement":
    """
    Overlay the building profile's defaults onto an existing element instance.

    Only parameters *already defined* on the element are overwritten.
    The element is re-validated after applying the profile.

    Returns the same (mutated) element object for convenient chaining.
    """
    element_type = element.element_type.lower()
    mapping = {
        "column":   profile.column_defaults,
        "beam":     profile.beam_defaults,
        "slab":     profile.slab_defaults,
        "footing":  profile.footing_defaults,
        "rebar":    profile.rebar_defaults,
        "studwall": profile.stud_wall_defaults,
    }
    defaults = mapping.get(element_type, {})
    for key, value in defaults.items():
        if hasattr(element, key):
            setattr(element, key, value)
    element.validate()
    return element


def create_element_with_profile(
    element_class,
    profile: BuildingProfile,
    overrides: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Convenience factory: instantiate an element class using profile defaults,
    then apply any caller-supplied overrides.

    Example
    -------
    col = create_element_with_profile(Column, RESIDENTIAL, overrides={"height": 4.0})
    """
    element_type = element_class.element_type.lower()
    profile_mapping = {
        "column":   profile.column_defaults,
        "beam":     profile.beam_defaults,
        "slab":     profile.slab_defaults,
        "footing":  profile.footing_defaults,
        "rebar":    profile.rebar_defaults,
        "studwall": profile.stud_wall_defaults,
    }
    params = dict(profile_mapping.get(element_type, {}))
    params.update(kwargs)
    if overrides:
        params.update(overrides)
    return element_class(**params)


# ===========================================================================
# ─── PROFILE DEFINITIONS ───────────────────────────────────────────────────
# ===========================================================================

RESIDENTIAL = BuildingProfile(
    name="Residential",
    description="Low-to-mid-rise residential buildings (G+3 to G+12, RC frame)",
    column_defaults={
        "shape": "rectangular", "width": 0.30, "depth": 0.30, "height": 3.0,
        "cover": 0.040, "num_bars": 8, "bar_diameter": 0.016,
        "tie_spacing": 0.150, "material": "concrete_m25",
    },
    beam_defaults={
        "width": 0.23, "depth": 0.45, "length": 4.5, "span_type": "simply_supported",
        "cover": 0.025, "bottom_bars": 3, "top_bars": 2,
        "bar_diameter": 0.016, "stirrup_dia": 0.008, "stirrup_spacing": 0.150,
        "material": "concrete_m25",
    },
    slab_defaults={
        "length": 4.5, "width": 4.0, "thickness": 0.125, "slab_type": "two_way",
        "cover": 0.020, "bar_diameter": 0.010, "bar_spacing": 0.150,
        "material": "concrete_m25",
    },
    footing_defaults={
        "footing_type": "isolated", "length": 1.5, "width": 1.5, "depth": 0.400,
        "cover": 0.050, "bar_diameter": 0.016, "bar_spacing": 0.200,
        "bearing_capacity": 150.0, "material": "concrete_m20",
    },
    rebar_defaults={
        "bar_type": "main", "diameter": 0.016, "length": 3.0,
        "num_bars": 4, "spacing": 0.150, "cover": 0.025,
        "material": "steel_fe415",
    },
    stud_wall_defaults={
        "length": 4.0, "height": 3.0, "stud_spacing": 0.400,
        "stud_width": 0.038, "stud_depth": 0.089,
        "sheathing_thick": 0.0125, "num_sheathing_layers": 1,
        "wall_type": "non_load_bearing", "stud_material": "timber",
        "material": "timber_douglas",
    },
)

AIRPORT = BuildingProfile(
    name="Airport",
    description="Large-span airport terminal / hangar structure",
    column_defaults={
        "shape": "circular", "diameter": 0.80, "height": 10.0,
        "cover": 0.050, "num_bars": 16, "bar_diameter": 0.025,
        "tie_spacing": 0.200, "material": "concrete_m40",
    },
    beam_defaults={
        "width": 0.60, "depth": 1.20, "length": 18.0, "span_type": "continuous",
        "cover": 0.040, "bottom_bars": 6, "top_bars": 4,
        "bar_diameter": 0.028, "stirrup_dia": 0.012, "stirrup_spacing": 0.200,
        "material": "concrete_m40",
    },
    slab_defaults={
        "length": 18.0, "width": 15.0, "thickness": 0.250, "slab_type": "flat_slab",
        "cover": 0.035, "bar_diameter": 0.016, "bar_spacing": 0.125,
        "material": "concrete_m40",
    },
    footing_defaults={
        "footing_type": "combined", "length": 4.0, "width": 4.0, "depth": 0.900,
        "cover": 0.075, "bar_diameter": 0.025, "bar_spacing": 0.150,
        "bearing_capacity": 300.0, "material": "concrete_m30",
    },
    rebar_defaults={
        "bar_type": "main", "diameter": 0.025, "length": 10.0,
        "num_bars": 16, "spacing": 0.125, "cover": 0.050,
        "material": "steel_fe500",
    },
    stud_wall_defaults={
        "length": 6.0, "height": 6.0, "stud_spacing": 0.400,
        "stud_width": 0.089, "stud_depth": 0.152,
        "sheathing_thick": 0.019, "num_sheathing_layers": 2,
        "wall_type": "fire_rated", "stud_material": "light_gauge_steel",
        "material": "steel_astm_a36",
    },
)

DATA_CENTER = BuildingProfile(
    name="Data_Center",
    description="Mission-critical data centre with raised-floor and heavy equipment loads",
    column_defaults={
        "shape": "rectangular", "width": 0.60, "depth": 0.60, "height": 5.0,
        "cover": 0.050, "num_bars": 12, "bar_diameter": 0.020,
        "tie_spacing": 0.100, "material": "concrete_m40",
    },
    beam_defaults={
        "width": 0.45, "depth": 0.90, "length": 9.0, "span_type": "continuous",
        "cover": 0.040, "bottom_bars": 4, "top_bars": 3,
        "bar_diameter": 0.025, "stirrup_dia": 0.010, "stirrup_spacing": 0.150,
        "material": "concrete_m40",
    },
    slab_defaults={
        "length": 9.0, "width": 9.0, "thickness": 0.200, "slab_type": "flat_plate",
        "cover": 0.025, "bar_diameter": 0.016, "bar_spacing": 0.125,
        "material": "concrete_m40",
    },
    footing_defaults={
        "footing_type": "mat", "length": 30.0, "width": 15.0, "depth": 0.750,
        "cover": 0.075, "bar_diameter": 0.020, "bar_spacing": 0.150,
        "bearing_capacity": 200.0, "material": "concrete_m30",
    },
    rebar_defaults={
        "bar_type": "main", "diameter": 0.020, "length": 5.0,
        "num_bars": 12, "spacing": 0.125, "cover": 0.040,
        "material": "steel_fe500",
    },
    stud_wall_defaults={
        "length": 5.0, "height": 5.0, "stud_spacing": 0.400,
        "stud_width": 0.041, "stud_depth": 0.102,
        "sheathing_thick": 0.016, "num_sheathing_layers": 2,
        "wall_type": "fire_rated", "stud_material": "light_gauge_steel",
        "material": "steel_astm_a36",
    },
)

INDUSTRIAL = BuildingProfile(
    name="Industrial",
    description="Heavy industrial plant / warehouse with large column grid",
    column_defaults={
        "shape": "rectangular", "width": 0.75, "depth": 0.75, "height": 8.0,
        "cover": 0.050, "num_bars": 16, "bar_diameter": 0.025,
        "tie_spacing": 0.200, "material": "concrete_m30",
    },
    beam_defaults={
        "width": 0.50, "depth": 1.00, "length": 12.0, "span_type": "simply_supported",
        "cover": 0.040, "bottom_bars": 5, "top_bars": 3,
        "bar_diameter": 0.025, "stirrup_dia": 0.012, "stirrup_spacing": 0.200,
        "material": "concrete_m30",
    },
    slab_defaults={
        "length": 12.0, "width": 8.0, "thickness": 0.200, "slab_type": "one_way",
        "cover": 0.030, "bar_diameter": 0.016, "bar_spacing": 0.200,
        "material": "concrete_m30",
    },
    footing_defaults={
        "footing_type": "isolated", "length": 3.0, "width": 3.0, "depth": 0.700,
        "cover": 0.075, "bar_diameter": 0.020, "bar_spacing": 0.175,
        "bearing_capacity": 250.0, "material": "concrete_m25",
    },
    rebar_defaults={
        "bar_type": "main", "diameter": 0.025, "length": 8.0,
        "num_bars": 16, "spacing": 0.200, "cover": 0.050,
        "material": "steel_fe500",
    },
    stud_wall_defaults={
        "length": 8.0, "height": 8.0, "stud_spacing": 0.600,
        "stud_width": 0.089, "stud_depth": 0.184,
        "sheathing_thick": 0.019, "num_sheathing_layers": 1,
        "wall_type": "non_load_bearing", "stud_material": "cold_formed_steel",
        "material": "steel_astm_a992",
    },
)

COMMERCIAL = BuildingProfile(
    name="Commercial",
    description="Commercial office tower (mid-to-high-rise, RC or composite frame)",
    column_defaults={
        "shape": "rectangular", "width": 0.50, "depth": 0.60, "height": 4.0,
        "cover": 0.040, "num_bars": 12, "bar_diameter": 0.020,
        "tie_spacing": 0.150, "material": "concrete_m30",
    },
    beam_defaults={
        "width": 0.35, "depth": 0.70, "length": 7.5, "span_type": "continuous",
        "cover": 0.030, "bottom_bars": 4, "top_bars": 3,
        "bar_diameter": 0.020, "stirrup_dia": 0.010, "stirrup_spacing": 0.175,
        "material": "concrete_m30",
    },
    slab_defaults={
        "length": 7.5, "width": 7.0, "thickness": 0.160, "slab_type": "two_way",
        "cover": 0.025, "bar_diameter": 0.012, "bar_spacing": 0.150,
        "material": "concrete_m30",
    },
    footing_defaults={
        "footing_type": "isolated", "length": 2.5, "width": 2.5, "depth": 0.600,
        "cover": 0.060, "bar_diameter": 0.020, "bar_spacing": 0.175,
        "bearing_capacity": 200.0, "material": "concrete_m25",
    },
    rebar_defaults={
        "bar_type": "main", "diameter": 0.020, "length": 4.0,
        "num_bars": 8, "spacing": 0.150, "cover": 0.030,
        "material": "steel_fe500",
    },
    stud_wall_defaults={
        "length": 5.0, "height": 4.0, "stud_spacing": 0.400,
        "stud_width": 0.041, "stud_depth": 0.102,
        "sheathing_thick": 0.013, "num_sheathing_layers": 1,
        "wall_type": "partition", "stud_material": "light_gauge_steel",
        "material": "steel_astm_a36",
    },
)

# All profiles in a handy list
ALL_PROFILES = [RESIDENTIAL, AIRPORT, DATA_CENTER, INDUSTRIAL, COMMERCIAL]
