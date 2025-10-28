from math import pi
from typing import Any

from geopandas import GeoDataFrame, GeoSeries
from shapely import Polygon

from ..config import EPSG_EQUAL_AREA, METERS_PER_KM


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check for the number of gaps between geometries."""
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        row = {"iso3": iso3, "version": version, "level": admin_level}
        if gdf.active_geometry_name:
            valid = gdf.copy()
            valid.geometry = valid.geometry.make_valid()
            interiors = valid.dissolve().explode().interiors.tolist()
            polygons = [Polygon(x) for y in interiors for x in y]
            if polygons:
                geometry = GeoSeries(polygons, crs=gdf.crs).to_crs(EPSG_EQUAL_AREA)
                thinness = geometry.map(lambda x: (4 * pi * x.area) / (x.length**2))
                row |= {
                    "geom_gap_area_km": geometry.area.min() / METERS_PER_KM,
                    "geom_gap_thinness": thinness.min(),
                }
            else:
                row |= {
                    "geom_gap_area_km": None,
                    "geom_gap_thinness": None,
                }
            check_results.append(row)
    return check_results
