"""
visualization.py
----------------
3-D visualization of parametric structural elements using matplotlib.

Uses mpl_toolkits.mplot3d to render colour-coded cuboid representations
of Columns, Beams, Slabs, Footings, Stud Walls, and Rebar sets.
"""

from __future__ import annotations
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D                      # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

if TYPE_CHECKING:
    from structural_element import StructuralElement


# ---------------------------------------------------------------------------
# Helper – build cuboid face polygons
# ---------------------------------------------------------------------------

def _cuboid_faces(
    ox: float, oy: float, oz: float,
    dx: float, dy: float, dz: float,
) -> List[List[Tuple[float, float, float]]]:
    """Return 6 faces of a cuboid as lists of 4 vertices."""
    x, y, z = ox, oy, oz
    x2, y2, z2 = ox + dx, oy + dy, oz + dz
    faces = [
        [(x,y,z),(x2,y,z),(x2,y2,z),(x,y2,z)],       # bottom
        [(x,y,z2),(x2,y,z2),(x2,y2,z2),(x,y2,z2)],   # top
        [(x,y,z),(x,y,z2),(x,y2,z2),(x,y2,z)],        # front
        [(x2,y,z),(x2,y,z2),(x2,y2,z2),(x2,y2,z)],   # back
        [(x,y,z),(x2,y,z),(x2,y,z2),(x,y,z2)],        # left
        [(x,y2,z),(x2,y2,z),(x2,y2,z2),(x,y2,z2)],   # right
    ]
    return faces


# ---------------------------------------------------------------------------
# Main visualiser class
# ---------------------------------------------------------------------------

class StructuralVisualizer:
    """
    Render a collection of structural elements in a 3-D matplotlib scene.

    Usage
    -----
    viz = StructuralVisualizer(title="Residential Building")
    viz.add_element(column)
    viz.add_element(beam)
    viz.show()           # interactive window
    viz.save("out.png")  # save to file
    """

    # Colour overrides per element type (fallback from geometry dict color)
    TYPE_COLORS = {
        "column":   "#4A90D9",   # steel blue
        "beam":     "#E07B39",   # burnt orange
        "slab":     "#7BC8A4",   # sage green
        "footing":  "#A0785A",   # earthy brown
        "rebar":    "#D4AF37",   # gold
        "stud_wall":"#C8A97E",   # tan/wood
    }

    def __init__(self, title: str = "Structural Elements – 3D View", figsize: Tuple = (14, 9)):
        self.title    = title
        self.figsize  = figsize
        self.elements: List["StructuralElement"] = []

    def add_element(self, element: "StructuralElement") -> None:
        self.elements.append(element)

    def add_elements(self, elements: List["StructuralElement"]) -> None:
        self.elements.extend(elements)

    # ------------------------------------------------------------------
    def _draw_element(self, ax: Axes3D, element: "StructuralElement") -> None:
        """Draw a single element on the given axes."""
        geom  = element.get_geometry()
        ox, oy, oz = geom["origin"]
        dims  = geom.get("dimensions", {})
        dx = dims.get("length", 0.5)
        dy = dims.get("width",  0.5)
        dz = dims.get("height", 0.5)

        color     = self.TYPE_COLORS.get(geom["type"], geom.get("color", "#AAAAAA"))
        faces     = _cuboid_faces(ox, oy, oz, dx, dy, dz)
        poly      = Poly3DCollection(faces, alpha=0.65, linewidths=0.5, edgecolors="white")
        poly.set_facecolor(color)
        ax.add_collection3d(poly)

        # Label at top-centre of element
        cx, cy, cz = ox + dx / 2, oy + dy / 2, oz + dz
        ax.text(
            cx, cy, cz + 0.05,
            element.label,
            fontsize=5.5,
            ha="center",
            color="black",
            weight="bold",
        )

    # ------------------------------------------------------------------
    def _legend_patches(self):
        """Build legend handles for element types present in the scene."""
        import matplotlib.patches as mpatches
        seen_types = {e.get_geometry()["type"] for e in self.elements}
        patches = []
        labels_map = {
            "column":   "Column",
            "beam":     "Beam",
            "slab":     "Slab",
            "footing":  "Footing",
            "rebar":    "Rebar",
            "stud_wall":"Stud Wall",
        }
        for etype in sorted(seen_types):
            color = self.TYPE_COLORS.get(etype, "#AAAAAA")
            patches.append(
                mpatches.Patch(facecolor=color, edgecolor="white",
                               label=labels_map.get(etype, etype.title()))
            )
        return patches

    # ------------------------------------------------------------------
    def _setup_axes(self, ax: Axes3D) -> None:
        """Compute scene bounds and set axis limits / labels."""
        if not self.elements:
            return

        xs, ys, zs = [], [], []
        for e in self.elements:
            geom = e.get_geometry()
            ox, oy, oz = geom["origin"]
            dims = geom.get("dimensions", {})
            xs += [ox, ox + dims.get("length", 0)]
            ys += [oy, oy + dims.get("width",  0)]
            zs += [oz, oz + dims.get("height", 0)]

        pad = 0.5
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.set_zlim(min(zs) - pad, max(zs) + pad)
        ax.set_xlabel("X (m)", labelpad=8)
        ax.set_ylabel("Y (m)", labelpad=8)
        ax.set_zlabel("Z (m)", labelpad=8)
        ax.set_title(self.title, fontsize=13, fontweight="bold", pad=12)
        ax.tick_params(labelsize=7)

    # ------------------------------------------------------------------
    def plot(self) -> plt.Figure:
        """Build and return the figure (does NOT display it)."""
        fig = plt.figure(figsize=self.figsize, facecolor="#1E1E2E")
        ax  = fig.add_subplot(111, projection="3d", facecolor="#1E1E2E")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.zaxis.label.set_color("white")
        ax.title.set_color("white")

        for e in self.elements:
            self._draw_element(ax, e)

        self._setup_axes(ax)
        patches = self._legend_patches()
        if patches:
            ax.legend(
                handles=patches,
                loc="upper left",
                fontsize=8,
                framealpha=0.4,
                facecolor="#2A2A3E",
                labelcolor="white",
            )
        fig.tight_layout()
        return fig

    def show(self) -> None:
        """Display the 3-D scene in an interactive window."""
        fig = self.plot()
        plt.show()
        plt.close(fig)

    def save(self, filepath: str, dpi: int = 150) -> None:
        """Save the 3-D scene to an image file."""
        fig = self.plot()
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"  ✔ Visualization saved → {filepath}")


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def visualize(
    elements: List["StructuralElement"],
    title: str = "Structural Elements",
    save_path: Optional[str] = None,
    show: bool = True,
) -> None:
    """
    One-line helper to visualise a list of structural elements.

    Parameters
    ----------
    elements  : list of StructuralElement instances
    title     : window / figure title
    save_path : optional file path to save the image (e.g. 'out.png')
    show      : if True, open an interactive matplotlib window
    """
    viz = StructuralVisualizer(title=title)
    viz.add_elements(elements)
    if save_path:
        viz.save(save_path)
    if show:
        viz.show()
