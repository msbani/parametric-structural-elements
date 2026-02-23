"""
main.py
-------
Demo entry-point for the Parametric Structural Elements System.

Demonstrates:
  1. Direct element instantiation with custom parameters
  2. Profile-driven element creation for 3 building types
  3. Console summaries for every element
  4. 3-D matplotlib visualisation (one figure per building type)
  5. JSON serialisation round-trip

Run:
    python main.py
"""

import json
import os
import sys

# Make sure project root is on Python path
sys.path.insert(0, os.path.dirname(__file__))

from structural_element import Position
from elements import Column, Beam, Slab, Footing, Rebar, StudWall
from building_profiles import (
    RESIDENTIAL, AIRPORT, DATA_CENTER,
    create_element_with_profile, ALL_PROFILES,
)
from visualization import visualize


# ===========================================================================
# Helper
# ===========================================================================

def section_header(title: str, width: int = 60) -> str:
    bar = "═" * width
    return f"\n{bar}\n  {title}\n{bar}"


def build_elements_for_profile(profile) -> list:
    """
    Create one of each structural element type using the given building profile.
    Positions are arranged so elements don't overlap in the 3-D view.
    """
    col = create_element_with_profile(
        Column, profile,
        position=Position(0.0, 0.0, 0.0),
        label=f"{profile.name}-Column",
    )
    beam = create_element_with_profile(
        Beam, profile,
        position=Position(0.0, 1.0, col.height),
        label=f"{profile.name}-Beam",
    )
    slab = create_element_with_profile(
        Slab, profile,
        position=Position(0.0, 0.0, col.height + beam.depth),
        label=f"{profile.name}-Slab",
    )
    footing = create_element_with_profile(
        Footing, profile,
        position=Position(0.0, 0.0, -footing_depth(profile)),
        label=f"{profile.name}-Footing",
    )
    rebar = create_element_with_profile(
        Rebar, profile,
        position=Position(0.1, 0.1, 0.1),
        label=f"{profile.name}-Rebar",
    )
    wall = create_element_with_profile(
        StudWall, profile,
        position=Position(1.5, 0.0, 0.0),
        label=f"{profile.name}-StudWall",
    )
    return [footing, col, beam, slab, rebar, wall]


def footing_depth(profile) -> float:
    return profile.footing_defaults.get("depth", 0.5)


# ===========================================================================
# 1. Residential Building
# ===========================================================================

def demo_residential():
    print(section_header("RESIDENTIAL BUILDING"))
    elements = build_elements_for_profile(RESIDENTIAL)
    for el in elements:
        print(el.summary())
    return elements


# ===========================================================================
# 2. Airport Terminal
# ===========================================================================

def demo_airport():
    print(section_header("AIRPORT TERMINAL"))
    elements = build_elements_for_profile(AIRPORT)
    for el in elements:
        print(el.summary())
    return elements


# ===========================================================================
# 3. Data Centre
# ===========================================================================

def demo_data_center():
    print(section_header("DATA CENTRE"))
    elements = build_elements_for_profile(DATA_CENTER)
    for el in elements:
        print(el.summary())
    return elements


# ===========================================================================
# 4. Custom element demo (mix-and-match parameters)
# ===========================================================================

def demo_custom():
    print(section_header("CUSTOM / AD-HOC ELEMENT DEMO"))

    # A bespoke circular column for a signature tower
    custom_col = Column(
        shape="circular",
        diameter=1.20,
        height=15.0,
        cover=0.060,
        num_bars=24,
        bar_diameter=0.032,
        tie_spacing=0.100,
        material="concrete_m40",
        position=Position(5.0, 5.0, -0.500),
        label="SignatureTower-CircularCol",
    )
    print(custom_col.summary())

    # A cantilever beam
    cantilever = Beam(
        width=0.40,
        depth=0.80,
        length=4.0,
        span_type="cantilever",
        bottom_bars=4,
        top_bars=5,
        bar_diameter=0.025,
        stirrup_spacing=0.100,
        material="concrete_m40",
        start_position=Position(5.0, 5.0, 15.0),
        label="SignatureTower-Cantilever",
    )
    print(cantilever.summary())

    # A waffle slab
    waffle = Slab(
        length=12.0,
        width=12.0,
        thickness=0.300,
        slab_type="waffle",
        bar_diameter=0.016,
        bar_spacing=0.200,
        material="concrete_m30",
        position=Position(5.0, 5.0, 15.8),
        label="SignatureTower-WaffleSlab",
    )
    print(waffle.summary())

    return [custom_col, cantilever, waffle]


# ===========================================================================
# 5. JSON serialisation round-trip
# ===========================================================================

def demo_serialization():
    print(section_header("JSON SERIALISATION ROUND-TRIP"))
    col = create_element_with_profile(
        Column, RESIDENTIAL, label="Serialisation-Test-Col"
    )
    original_dict = col.to_dict()
    json_str = json.dumps(original_dict, indent=2)
    print("  Serialised JSON:")
    print("  " + "\n  ".join(json_str.splitlines()))

    # Rebuild from dict
    restored = Column.from_dict(dict(original_dict))
    match = (
        restored.height == col.height
        and restored.width  == col.width
        and restored.material == col.material
    )
    print(f"\n  Round-trip match: {'✔ PASS' if match else '✘ FAIL'}")


# ===========================================================================
# 6. Profile Comparison Table
# ===========================================================================

def demo_profile_comparison():
    print(section_header("PROFILE COMPARISON — COLUMN DEFAULTS"))
    header = f"  {'Profile':<18} {'Shape':<13} {'W×D or Dia (mm)':<20} {'Height (m)':<12} {'Material'}"
    print(header)
    print("  " + "─" * 72)
    for prof in ALL_PROFILES:
        cd = prof.column_defaults
        shape = cd.get("shape", "rectangular")
        if shape == "circular":
            dims = f"Ø{cd.get('diameter',0)*1000:.0f}"
        else:
            dims = f"{cd.get('width',0)*1000:.0f}×{cd.get('depth',0)*1000:.0f}"
        h   = cd.get("height", 0)
        mat = cd.get("material", "—")
        print(f"  {prof.name:<18} {shape:<13} {dims:<20} {h:<12} {mat}")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "▐" * 60)
    print("  PARAMETRIC STRUCTURAL ELEMENTS SYSTEM")
    print("  Generalized BIM / Structural Engineering Tool")
    print("▐" * 60)

    res_elements  = demo_residential()
    air_elements  = demo_airport()
    dc_elements   = demo_data_center()
    cust_elements = demo_custom()
    demo_serialization()
    demo_profile_comparison()

    # ── Visualisation ──────────────────────────────────────────────────
    print(section_header("3-D VISUALISATION"))
    print("  Generating figures… (close each window to proceed to the next)")

    output_dir = os.path.dirname(__file__)

    # Residential
    print("  [1/3] Residential building…")
    visualize(
        res_elements,
        title="Residential Building — Structural Elements",
        save_path=os.path.join(output_dir, "output_residential.png"),
        show=True,
    )

    # Airport
    print("  [2/3] Airport terminal…")
    visualize(
        air_elements,
        title="Airport Terminal — Structural Elements",
        save_path=os.path.join(output_dir, "output_airport.png"),
        show=True,
    )

    # Data Centre
    print("  [3/3] Data centre…")
    visualize(
        dc_elements,
        title="Data Centre — Structural Elements",
        save_path=os.path.join(output_dir, "output_data_center.png"),
        show=True,
    )

    print("\n  All done! PNG files saved to the project directory.")
    print("▐" * 60 + "\n")
