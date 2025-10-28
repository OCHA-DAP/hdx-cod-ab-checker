from pathlib import Path
from re import search

from geopandas import read_parquet

from .config import ARCGIS_LAYER_REGEX, data_dir
from .utils import is_iso3_allowed


def create_csv(input_path: Path) -> None:
    """Create a CSV for an admin boundary."""
    csv = data_dir / "attributes" / input_path.parent.name / f"{input_path.stem}.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    gdf = read_parquet(input_path)
    gdf.drop(columns="geometry").to_csv(csv, index=False, encoding="utf-8-sig")


def main() -> None:
    """Create a csv and image for each administrative boundary layer."""
    latest_dir = data_dir / "boundaries"
    for input_path in sorted(latest_dir.rglob("*.parquet")):
        iso3 = input_path.stem[0:3].upper()
        if search(ARCGIS_LAYER_REGEX, input_path.stem) and is_iso3_allowed(iso3):
            create_csv(input_path)
