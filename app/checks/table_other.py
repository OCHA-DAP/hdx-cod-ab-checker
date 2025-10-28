from re import match
from typing import Any

from geopandas import GeoDataFrame


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check completeness of an admin boundary by checking the columns."""
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        name_columns = [
            column
            for column in gdf.columns
            for level in range(admin_level + 1)
            if match(rf"^adm{level}_name\d?$", column)
        ]
        pcode_columns = [
            column
            for column in gdf.columns
            for level in range(admin_level + 1)
            if column == f"adm{level}_pcode"
        ]
        iso_columns = [x for x in gdf.columns if x in ["iso3", "iso2"]]
        center_columns = [x for x in gdf.columns if x in ["center_lat", "center_lon"]]
        version_columns = [x for x in gdf.columns if x in ["cod_version", "version"]]
        metadata_columns = [
            "geometry",
            "valid_on",
            "valid_to",
            "area_sqkm",
            "lang",
            "lang1",
            "lang2",
            "lang3",
        ]
        ref_name_columns = [
            x for x in gdf.columns if match(rf"^adm{admin_level}_ref", x)
        ]
        valid_columns = (
            name_columns
            + pcode_columns
            + version_columns
            + iso_columns
            + center_columns
            + metadata_columns
            + ref_name_columns
        )
        other_columns = [x for x in gdf.columns if x not in valid_columns]
        row = {
            "iso3": iso3,
            "version": version,
            "level": admin_level,
            "version_column_count": len(version_columns),
            "version_columns": ",".join(version_columns),
            "iso_column_count": len(iso_columns),
            "iso_columns": ",".join(iso_columns),
            "center_column_count": len(center_columns),
            "center_columns": ",".join(center_columns),
            "ref_name_column_count": len(ref_name_columns),
            "ref_name_columns": ",".join(ref_name_columns),
            "other_column_count": len(other_columns),
            "other_columns": ",".join(other_columns),
        }
        check_results.append(row)
    return check_results
