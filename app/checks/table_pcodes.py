from typing import Any

from geopandas import GeoDataFrame
from pycountry import countries

from ..utils import is_empty


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check completeness of an admin boundary by checking the columns."""

    def not_iso2(value: str | None) -> bool:
        country = countries.get(alpha_3=iso3)
        if country and value and value.strip():
            iso2 = country.alpha_2
            return not value.startswith(iso2)
        return False

    def not_iso(value: str | None) -> bool:
        country = countries.get(alpha_3=iso3)
        if country and value and value.strip():
            return not value.startswith(country.alpha_2) and not value.startswith(iso3)
        return False

    def not_alnum(value: str | None) -> bool:
        if value and value.strip():
            return not value.isalnum()
        return False

    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        pcode_columns = [
            column
            for column in gdf.columns
            for level in range(admin_level + 1)
            if column == f"adm{level}_pcode"
        ]
        pcodes = gdf[pcode_columns]
        row = {
            "iso3": iso3,
            "version": version,
            "level": admin_level,
            "pcode_column_levels": len(pcode_columns),
            "pcode_cell_count": max(pcodes.size, 1),
            "pcode_empty": (pcodes.isna() | pcodes.map(is_empty)).sum().sum(),
            "pcode_not_iso2": pcodes.map(not_iso2).sum().sum(),
            "pcode_not_iso": pcodes.map(not_iso).sum().sum(),
            "pcode_not_alnum": pcodes.map(not_alnum).sum().sum(),
            "pcode_lengths": 0,
            "pcode_duplicated": 0,
            "pcode_not_nested": 0,
        }
        pcode_self = f"adm{admin_level}_pcode"
        pcode_parent = f"adm{admin_level - 1}_pcode"
        if pcode_self in pcode_columns:
            self_series = pcodes[pcode_self]
            series = self_series[~self_series.isna() & ~self_series.map(is_empty)]
            row["pcode_lengths"] = series.map(len).nunique()
            row["pcode_duplicated"] = series.duplicated().sum()
            if pcode_parent in pcode_columns:
                row["pcode_not_nested"] = pcodes.apply(
                    lambda row, pcode_self=pcode_self, pcode_parent=pcode_parent: (
                        not row[pcode_self].startswith(row[pcode_parent])
                        if row[pcode_self]
                        and row[pcode_self].strip()
                        and row[pcode_parent]
                        and row[pcode_parent].strip()
                        else False
                    ),
                    axis=1,
                ).sum()
        check_results.append(row)
    return check_results
