from re import match
from typing import Any

from geopandas import GeoDataFrame

from ..utils import is_empty
from .table_names_utils import (
    get_invalid_chars,
    has_double_spaces,
    has_strippable_spaces,
    is_invalid,
    is_invalid_adm0,
    is_lower,
    is_punctuation,
    is_upper,
)


def main(iso3: str, version: str, gdfs: list[GeoDataFrame]) -> list[dict[str, Any]]:
    """Check completeness of an admin boundary by checking the columns."""
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        name_lang_columns = [
            (f"adm{level}_name{index}", gdf[f"lang{index}"].iloc[0])
            for index in ["", "1", "2", "3"]
            for level in range(admin_level + 1)
            if f"lang{index}" in gdf.columns and gdf[f"lang{index}"].notna().any()
        ]
        name_columns = [col for col, _ in name_lang_columns]
        adm0_names = [x for x in name_lang_columns if x[0] == "adm0_name"]
        invalid_chars = "".join(
            {
                gdf[col]
                .map(lambda x, lang=lang: get_invalid_chars(lang, x, iso3))
                .sum()
                for col, lang in name_lang_columns
            },
        )

        row = {
            "iso3": iso3,
            "version": version,
            "level": admin_level,
            "name_column_levels": sum(
                [
                    any(
                        bool(match(rf"^adm{level}_name\d?$", column))
                        for column in gdf.columns
                    )
                    for level in range(admin_level + 1)
                ],
            ),
            "name_column_count": len(name_columns),
            "name_cell_count": max(gdf[name_columns].size, 1),
            "name_empty": (gdf[name_columns].isna() | gdf[name_columns].map(is_empty))
            .sum()
            .sum(),
            "name_duplicated": gdf[name_columns].duplicated().sum().sum(),
            "name_spaces_strip": sum(
                [gdf[col].map(has_strippable_spaces).sum() for col in name_columns],
            ),
            "name_spaces_double": sum(
                [gdf[col].map(has_double_spaces).sum() for col in name_columns],
            ),
            "name_upper": sum(
                [gdf[col].map(is_upper).sum() for col in name_columns],
            ),
            "name_lower": sum(
                [gdf[col].map(is_lower).sum() for col in name_columns],
            ),
            "name_no_valid": sum(
                [
                    gdf[col]
                    .map(lambda x, lang=lang: is_punctuation(lang, x, iso3))
                    .sum()
                    for col, lang in name_lang_columns
                ],
            ),
            "name_invalid_adm0": sum(
                [
                    gdf[col]
                    .map(lambda x, lang=lang: is_invalid_adm0(lang, x, iso3))
                    .any()
                    for col, lang in adm0_names
                ],
            ),
            "name_invalid": sum(
                [
                    gdf[col].map(lambda x, lang=lang: is_invalid(lang, x, iso3)).sum()
                    for col, lang in name_lang_columns
                ],
            ),
            "name_invalid_char_count": len({*list(invalid_chars)}),
            "name_invalid_chars": ",".join(
                sorted({f"U+{ord(x):04X}" for x in invalid_chars}),
            ),
        }
        check_results.append(row)
    return check_results
