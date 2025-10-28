from typing import Any

from geopandas import GeoDataFrame


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check for the number of self-overlaping geometries.

    Conducting a spatial join predicated by overlaps is very computationally expensive.
    This module has been separated out from other geometry checks so that it can be made
    optional.
    """
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        if gdf.active_geometry_name:
            overlaps = gdf.sjoin(gdf, predicate="overlaps")
            overlap_count = len(overlaps[overlaps.index != overlaps.index_right].index)
            row = {
                "iso3": iso3,
                "version": version,
                "level": admin_level,
                "geom_overlaps_self": overlap_count / 2,
            }
            check_results.append(row)
    return check_results
