from typing import Any

from geopandas import GeoDataFrame


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check for unique date values within dataset.

    There are two date fields within each COD-AB, "valid_on" and "valid_to". "valid_on"
    represents when this dataset was last changed throughout the data update lifecycle.
    "valid_to" is null if the current dataset is the latest version, otherwise it
    specifies the retirement date of that version. If there are multiple unique values
    for dates within the dataset, they will be listed in separate output columns:
    "valid_on_1", "valid_on_2", etc.
    """
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        row = {
            "iso3": iso3,
            "version": version,
            "level": admin_level,
            "valid_to_exists": 0,
            "valid_to_empty": 0,
            "valid_on_count": 0,
        }
        try:
            gdf_update = gdf[~gdf["valid_on"].isna()]["valid_on"].drop_duplicates()
            for index, value in enumerate(gdf_update):
                row["valid_on_count"] += 1
                row[f"valid_on_{index + 1}"] = value
        except KeyError:
            pass
        if "valid_to" in gdf.columns:
            row["valid_to_exists"] = 1
            if gdf["valid_to"].isna().all():
                row["valid_to_empty"] = 1
        check_results.append(row)
    return check_results
