# Parametric Structural Elements System

A generalized, parametric, object-oriented Python library for **BIM and structural engineers** to define, validate, and visualize structural elements across different building types — all from simple parameters.

---

## Features

- ✅ **6 Parametric Element Types** — Column, Beam, Slab, Footing, Rebar, Stud Wall
- 🏗️ **5 Built-in Building Profiles** — Residential, Airport, Data Center, Industrial, Commercial
- 🔢 **Engineering Calculations** — Steel ratios, effective depth, concrete volume, load capacity, weights
- 🎨 **3D Visualization** — Color-coded dark-themed matplotlib 3D scene with labels & legend
- 🔄 **JSON Serialization** — Export/import element definitions with `to_dict()` / `from_dict()`
- 🧪 **43 Unit Tests** — Full test coverage on validation, calculations, and profile system

---

## Project Structure

```
Structural Components/
│
├── structural_element.py       # Abstract base class + material catalogue
├── building_profiles.py        # Pre-defined building type profiles
├── visualization.py            # 3D matplotlib renderer
├── main.py                     # Demo / entry point
│
├── elements/
│   ├── column.py               # Rectangular & circular columns
│   ├── beam.py                 # Simply supported / continuous / cantilever beams
│   ├── slab.py                 # One-way, two-way, flat plate, waffle, ribbed slabs
│   ├── footing.py              # Isolated, combined, strip, mat, pile cap footings
│   ├── rebar.py                # Main bars, stirrups, ties, mesh, spirals
│   └── stud_wall.py            # Timber & light-gauge steel stud walls
│
└── tests/
    └── test_elements.py        # 43 unit tests
```

---

## Quick Start

### Requirements

```
python >= 3.9
matplotlib
numpy
```

Install dependencies:

```bash
pip install matplotlib numpy
```

### Run the Demo

```bash
python main.py
```

This will:
1. Print detailed text summaries for Residential, Airport and Data Centre building types
2. Show a custom element demo (circular signature column, cantilever beam, waffle slab)
3. Open 3 interactive 3D matplotlib windows and save them as PNG files

---

## Usage Examples

### Profile-Driven (Recommended)

```python
from elements import Column, Beam, Slab
from building_profiles import AIRPORT, create_element_with_profile
from structural_element import Position

# Create an airport column — override just the height
col = create_element_with_profile(
    Column, AIRPORT,
    overrides={"height": 12.0},
    position=Position(0, 0, 0),
    label="Terminal-Col-A1"
)
print(col.summary())
```

### Fully Custom

```python
from elements import Column
from structural_element import Position

col = Column(
    shape="circular",
    diameter=1.20,
    height=15.0,
    cover=0.060,
    num_bars=24,
    bar_diameter=0.032,
    tie_spacing=0.100,
    material="concrete_m40",
    position=Position(5.0, 5.0, 0.0),
    label="Signature-Tower-Col",
)
print(col.summary())
```

### Apply Profile to Existing Element

```python
from elements import Column
from building_profiles import DATA_CENTER, apply_profile

col = Column(height=3.0)            # start with a custom value
apply_profile(col, DATA_CENTER)     # overlay data-centre defaults
```

### Visualization

```python
from visualization import visualize
visualize(elements, title="My Building", save_path="output.png", show=True)
```

---

## Building Profiles

| Profile | Column | Slab Type | Typical Application |
|---|---|---|---|
| **Residential** | 300×300 mm RC | Two-way | G+3 to G+12 apartments |
| **Airport** | Ø800 mm circular | Flat slab | Large-span terminals |
| **Data_Center** | 600×600 mm RC | Flat plate | Mission-critical floors |
| **Industrial** | 750×750 mm RC | One-way | Warehouses, factories |
| **Commercial** | 500×600 mm RC | Two-way | Office towers |

---

## Material Catalogue

| Key | Material | Grade |
|---|---|---|
| `concrete_m20` | Concrete M20 | fc = 20 MPa |
| `concrete_m25` | Concrete M25 | fc = 25 MPa |
| `concrete_m30` | Concrete M30 | fc = 30 MPa |
| `concrete_m40` | Concrete M40 | fc = 40 MPa |
| `steel_fe415` | Steel Fe415 | fy = 415 MPa |
| `steel_fe500` | Steel Fe500 | fy = 500 MPa |
| `timber_douglas` | Douglas Fir | fb = 12 MPa |
| `steel_astm_a36` | ASTM A36 | fy = 250 MPa |
| `steel_astm_a992` | ASTM A992 | fy = 345 MPa |

---

## Running Tests

```bash
python -m unittest discover -s tests -v
```

**Result: 43 tests, 0 failures**

