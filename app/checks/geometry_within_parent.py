from typing import Any

from geopandas import GeoDataFrame


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check for the number of geometries within a parent layer.

    If a dataset is perfectly hierarchally nested, each geometry will fall within a
    parent geometry.
    """
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        if gdf.active_geometry_name:
            if admin_level == 0:
                row = {
                    "iso3": iso3,
                    "version": version,
                    "level": admin_level,
                    "geom_not_within_parent": 0,
                }
                check_results.append(row)
            else:
                parent = gdfs[admin_level - 1]
                if parent.active_geometry_name:
                    within = gdf.sjoin(parent, predicate="within")
                    row = {
                        "iso3": iso3,
                        "version": version,
                        "level": admin_level,
                        "geom_not_within_parent": len(gdf.index) - len(within.index),
                    }
                    pcode_left = f"adm{admin_level - 1}_pcode_left"
                    pcode_right = f"adm{admin_level - 1}_pcode_right"
                    if all(x in within.columns for x in [pcode_left, pcode_right]):
                        pcode = within[within[pcode_left].eq(within[pcode_right])]
                        row |= {
                            "geom_not_within_pcode": len(within.index)
                            - len(pcode.index),
                        }
                    check_results.append(row)
    return check_results
