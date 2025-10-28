from pandas import DataFrame


def main(checks: DataFrame) -> DataFrame:
    """Scores columns used within dataset.

    Layers which have no other columns.

    Args:
        checks: checks DataFrame.

    Returns:
        Checks DataFrame with additional columns for scoring.

    """
    scores = checks[["iso3", "version", "level"]].copy()
    scores["other"] = checks["version_column_count"].eq(1) & checks[
        "center_column_count"
    ].eq(2)
    return scores
