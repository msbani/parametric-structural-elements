"""
tests/test_elements.py
----------------------
Unit tests for all parametric structural element classes.
Run with:  python -m pytest tests/ -v
"""

import math
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from structural_element import Position, MATERIALS
from elements import Column, Beam, Slab, Footing, Rebar, StudWall
from building_profiles import (
    RESIDENTIAL, AIRPORT, DATA_CENTER, INDUSTRIAL, COMMERCIAL,
    apply_profile, create_element_with_profile, BuildingProfile, ALL_PROFILES,
)


# ===========================================================================
# Column tests
# ===========================================================================

class TestColumn(unittest.TestCase):

    def test_rectangular_defaults(self):
        col = Column()
        self.assertEqual(col.shape, "rectangular")
        self.assertGreater(col.cross_section_area(), 0)
        self.assertIn("Column", col.label)

    def test_circular_column(self):
        col = Column(shape="circular", diameter=0.60, height=4.0)
        expected_area = math.pi * 0.09
        self.assertAlmostEqual(col.cross_section_area(), expected_area, places=4)

    def test_volume(self):
        col = Column(width=0.30, depth=0.30, height=3.0)
        self.assertAlmostEqual(col.volume(), 0.27, places=4)

    def test_steel_ratio_bounds(self):
        col = Column()
        # IS 456 requires 0.8% to 6% for RC columns
        self.assertGreater(col.steel_ratio(), 0.004)
        self.assertLess(col.steel_ratio(), 0.08)

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            Column(shape="triangular")

    def test_invalid_min_bars(self):
        with self.assertRaises(ValueError):
            Column(num_bars=2)

    def test_cover_too_large(self):
        with self.assertRaises(ValueError):
            Column(width=0.10, depth=0.10, cover=0.06)  # cover > w/2

    def test_to_dict(self):
        col = Column(label="TestCol")
        d = col.to_dict()
        self.assertEqual(d["element_type"], "Column")
        self.assertEqual(d["label"], "TestCol")
        self.assertIn("position", d)

    def test_from_dict_roundtrip(self):
        col = Column(height=5.0, width=0.50, depth=0.50, label="RT")
        d   = col.to_dict()
        r   = Column.from_dict(dict(d))
        self.assertAlmostEqual(r.height, col.height)
        self.assertAlmostEqual(r.width,  col.width)

    def test_summary_is_string(self):
        self.assertIsInstance(Column().summary(), str)


# ===========================================================================
# Beam tests
# ===========================================================================

class TestBeam(unittest.TestCase):

    def test_defaults(self):
        b = Beam()
        self.assertGreater(b.volume(), 0)

    def test_effective_depth(self):
        b = Beam(depth=0.60, cover=0.025, stirrup_dia=0.010, bar_diameter=0.020)
        expected = 0.60 - 0.025 - 0.010 - 0.010   # cover + stirrup + bar/2
        self.assertAlmostEqual(b.effective_depth(), expected, places=4)

    def test_invalid_span_type(self):
        with self.assertRaises(ValueError):
            Beam(span_type="arch")

    def test_invalid_orientation(self):
        with self.assertRaises(ValueError):
            Beam(orientation="z")

    def test_num_stirrups(self):
        b = Beam(length=3.0, stirrup_spacing=0.150)
        self.assertGreaterEqual(b.num_stirrups(), 1)

    def test_geometry_keys(self):
        g = Beam().get_geometry()
        self.assertIn("type", g)
        self.assertIn("dimensions", g)
        self.assertIn("origin", g)


# ===========================================================================
# Slab tests
# ===========================================================================

class TestSlab(unittest.TestCase):

    def test_volume(self):
        s = Slab(length=6.0, width=5.0, thickness=0.150)
        self.assertAlmostEqual(s.volume(), 4.5, places=4)

    def test_span_ratio(self):
        s = Slab(length=8.0, width=4.0)
        self.assertAlmostEqual(s.span_ratio(), 2.0, places=2)

    def test_invalid_slab_type(self):
        with self.assertRaises(ValueError):
            Slab(slab_type="dome")

    def test_cover_validation(self):
        with self.assertRaises(ValueError):
            Slab(thickness=0.120, cover=0.070)  # cover > thickness/2

    def test_plan_area(self):
        s = Slab(length=5.0, width=4.0)
        self.assertAlmostEqual(s.plan_area(), 20.0, places=3)


# ===========================================================================
# Footing tests
# ===========================================================================

class TestFooting(unittest.TestCase):

    def test_defaults(self):
        f = Footing()
        self.assertGreater(f.volume(), 0)

    def test_safe_load_capacity(self):
        f = Footing(length=2.0, width=2.0, bearing_capacity=150.0)
        self.assertAlmostEqual(f.safe_load_capacity(), 600.0, places=1)

    def test_invalid_footing_type(self):
        with self.assertRaises(ValueError):
            Footing(footing_type="cantilever")

    def test_effective_depth(self):
        f = Footing(depth=0.500, cover=0.050, bar_diameter=0.016)
        expected = 0.500 - 0.050 - 0.008
        self.assertAlmostEqual(f.effective_depth(), expected, places=4)

    def test_negative_bearing_capacity(self):
        with self.assertRaises(ValueError):
            Footing(bearing_capacity=-10)


# ===========================================================================
# Rebar tests
# ===========================================================================

class TestRebar(unittest.TestCase):

    def test_bar_area(self):
        r = Rebar(diameter=0.016)
        expected = math.pi * 0.008 ** 2
        self.assertAlmostEqual(r.bar_area(), expected, places=8)

    def test_total_weight_positive(self):
        r = Rebar(diameter=0.016, length=3.0, num_bars=8)
        self.assertGreater(r.total_weight(), 0)

    def test_nearest_standard_dia(self):
        r = Rebar(diameter=0.016)
        self.assertEqual(r.nearest_standard_dia(), 16)

    def test_invalid_bar_type(self):
        with self.assertRaises(ValueError):
            Rebar(bar_type="hook")

    def test_hook_length_adds_to_total(self):
        r_no_hook = Rebar(length=3.0, hook_length=0.0)
        r_hook    = Rebar(length=3.0, hook_length=0.150)
        self.assertGreater(r_hook.total_length(), r_no_hook.total_length())


# ===========================================================================
# StudWall tests
# ===========================================================================

class TestStudWall(unittest.TestCase):

    def test_total_thickness(self):
        sw = StudWall(stud_depth=0.089, sheathing_thick=0.0125, num_sheathing_layers=1)
        expected = 0.089 + 2 * 1 * 0.0125
        self.assertAlmostEqual(sw.total_thickness(), expected, places=4)

    def test_num_studs(self):
        sw = StudWall(length=4.0, stud_spacing=0.400)
        self.assertGreaterEqual(sw.num_studs(), 2)

    def test_invalid_wall_type(self):
        with self.assertRaises(ValueError):
            StudWall(wall_type="curtain")

    def test_invalid_stud_material(self):
        with self.assertRaises(ValueError):
            StudWall(stud_material="concrete")

    def test_face_area(self):
        sw = StudWall(length=4.0, height=3.0)
        self.assertAlmostEqual(sw.face_area(), 12.0, places=3)


# ===========================================================================
# Building Profiles tests
# ===========================================================================

class TestBuildingProfiles(unittest.TestCase):

    def test_all_profiles_loaded(self):
        self.assertEqual(len(ALL_PROFILES), 5)

    def test_profile_registry(self):
        p = BuildingProfile.get("Residential")
        self.assertEqual(p.name, "Residential")

    def test_create_column_with_residential_profile(self):
        col = create_element_with_profile(Column, RESIDENTIAL)
        self.assertIsInstance(col, Column)
        self.assertEqual(col.material, RESIDENTIAL.column_defaults["material"])

    def test_create_column_with_airport_profile(self):
        col = create_element_with_profile(Column, AIRPORT)
        self.assertEqual(col.shape, "circular")

    def test_apply_profile_override(self):
        col = Column(height=3.0)
        apply_profile(col, AIRPORT)
        self.assertEqual(col.height, AIRPORT.column_defaults["height"])

    def test_override_beats_profile(self):
        col = create_element_with_profile(
            Column, RESIDENTIAL, overrides={"height": 99.0}
        )
        self.assertAlmostEqual(col.height, 99.0)

    def test_data_center_slab_flat_plate(self):
        slab = create_element_with_profile(Slab, DATA_CENTER)
        self.assertEqual(slab.slab_type, "flat_plate")


# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
