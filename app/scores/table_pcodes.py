from pandas import DataFrame


def main(checks: DataFrame) -> DataFrame:
    """Scores columns used within dataset.

    Layers which have all required P-Code columns (ADM2_PCODE), with no empty cells,
    only alphanumeric characters, starting with a valid ISO-2 code, and hierarchical
    nesting codes.

    Args:
        checks: checks DataFrame.

    Returns:
        Checks DataFrame with additional columns for scoring.

    """
    scores = checks[["iso3", "version", "level"]].copy()
    scores["pcode_all_levels"] = checks["pcode_column_levels"].eq(checks["level"] + 1)
    scores["pcode_not_empty"] = checks["pcode_empty"].eq(0)
    scores["pcode_iso_start"] = checks["pcode_not_iso"].eq(0)
    scores["pcode_alnum"] = checks["pcode_not_alnum"].eq(0)
    scores["pcode_fixed_length"] = checks["pcode_lengths"].eq(1)
    scores["pcode_unique"] = checks["pcode_duplicated"].eq(0)
    scores["pcode_nested"] = checks["pcode_not_nested"].eq(0)
    return scores
