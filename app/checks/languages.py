from typing import Any

from geopandas import GeoDataFrame
from langcodes import tag_is_valid


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check for which languages are used within dataset.

    Datasets use the following pattern in their field names for identifying languages:
    "ADM{LEVEL}_{LANGUAGE_CODE}". For example, a dataset containing English, French,
    and Haitian Creole for admin level 1 would have the following field names:
    ADM1_EN, ADM1_FR, ADM1_HT. Regex is used to identify field names, this may pick up
    columns such as identification fields if they are named like ADM1_ID. However, this
    would be a valid column if it was used for Indonesian names.

    The following are a list of source and output columns:
    - source: "ADM{LEVEL}_{LANGUAGE_CODE}"
        - output: "language_count", "language_1", "language_2", "language_3", etc...
    """
    check_results = []
    language_parent = None
    for admin_level, gdf in enumerate(gdfs):
        row = {
            "iso3": iso3,
            "version": version,
            "level": admin_level,
            "language_count": 0,
            "language_parent": language_parent,
            "language_invalid": 0,
        }
        langs = [
            gdf[f"lang{index}"].iloc[0]
            for index in ["", "1", "2", "3"]
            if f"lang{index}" in gdf.columns and gdf[f"lang{index}"].notna().any()
        ]
        for index, lang in enumerate(langs):
            row["language_count"] += 1
            row[f"language_{index + 1}"] = lang
            if not tag_is_valid(lang):
                row["language_invalid"] += 1
        language_parent = row["language_count"]
        check_results.append(row)
    return check_results
