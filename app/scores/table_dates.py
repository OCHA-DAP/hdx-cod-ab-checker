from pandas import DataFrame


def main(checks: DataFrame) -> DataFrame:
    """Score date values within dataset."""
    scores = checks[["iso3", "version", "level"]].copy()
    group = checks[["iso3", "valid_on_1"]].groupby("iso3").agg(["count", "nunique"])
    group.columns = group.columns.get_level_values(1)
    group["valid_on_all_equal"] = (group["count"] - group["nunique"] + 1) / group[
        "count"
    ]
    scores = scores.merge(group["valid_on_all_equal"], on="iso3")
    scores["valid_on_self_equal"] = checks["valid_on_count"].eq(1)
    scores["valid_to"] = checks["valid_to_exists"].eq(1) & (
        (checks["version"].isna() & checks["valid_to_empty"].eq(1))
        | checks["version"].notna()
    )
    return scores
