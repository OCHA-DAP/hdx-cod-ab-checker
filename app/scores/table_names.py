from pandas import DataFrame


def main(checks: DataFrame) -> DataFrame:
    """Scores columns used within dataset.

    Gives a perfect score to layers which have all required name columns (ADM2_EN), with
    no empty cells, no columns all uppercase, no cells lacking alphabetic characters,
    and all characters matching the language code.

    Args:
        checks: checks DataFrame.

    Returns:
        Checks DataFrame with additional columns for scoring.

    """
    scores = checks[["iso3", "version", "level"]].copy()
    scores["name_all_levels"] = checks["name_column_levels"].eq(
        checks["level"] + 1,
    ) & checks["name_column_count"].ge(
        checks["language_count"] * (checks["level"] + 1),
    )
    scores["name_not_empty"] = checks["name_empty"].eq(0)
    scores["name_unique"] = checks["name_duplicated"].eq(0)
    scores["name_no_extra_spaces"] = checks["name_spaces_double"].eq(0) & checks[
        "name_spaces_strip"
    ].eq(0)
    scores["name_proper_case"] = (
        checks["name_upper"] * checks["name_column_count"]
    ).lt(checks["name_cell_count"]) & (
        checks["name_lower"] * checks["name_column_count"]
    ).lt(checks["name_cell_count"])
    scores["name_has_characters"] = checks["name_no_valid"].eq(0)
    scores["name_valid"] = checks["name_invalid"].eq(0)
    scores["name_valid_adm0"] = checks["name_invalid_adm0"].eq(0)
    return scores
