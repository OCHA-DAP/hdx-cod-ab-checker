from pathlib import Path
from re import search

import matplotlib.pyplot as plt
from geopandas import read_parquet

from .config import ARCGIS_LAYER_REGEX, data_dir
from .utils import is_iso3_allowed

pixels = 1000
dpi = 100
figsize_inches = pixels / dpi


def create_png(input_path: Path) -> None:
    """Create a PNG for an admin boundary."""
    png = data_dir / "images" / input_path.parent.name / f"{input_path.stem}.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    gdf = read_parquet(input_path)
    fig, ax = plt.subplots(figsize=(figsize_inches, figsize_inches))
    gdf.plot(ax=ax, edgecolor="white", linewidth=0.3)
    ax.set_axis_off()
    fig.savefig(png, dpi=dpi, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close(fig)


def main() -> None:
    """Create a csv and image for each administrative boundary layer."""
    boundaries_dir = data_dir / "boundaries"
    for input_path in sorted(boundaries_dir.rglob("*.parquet")):
        iso3 = input_path.stem[0:3].upper()
        if search(ARCGIS_LAYER_REGEX, input_path.stem) and is_iso3_allowed(iso3):
            create_png(input_path)
