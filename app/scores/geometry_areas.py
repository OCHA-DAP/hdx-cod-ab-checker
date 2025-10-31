from pandas import DataFrame


def main(checks: DataFrame) -> DataFrame:
    """Create scores based on geometry area."""
    scores = checks[["iso3", "version", "level"]].copy()
    group = (
        checks[["iso3", "version", "geom_area_km"]]
        .groupby(["iso3", "version"])
        .agg(["count", "nunique"])
    )
    group.columns = group.columns.get_level_values(1)
    group["geometry_area"] = (group["count"] - group["nunique"] + 1) / group["count"]
    return scores.merge(group["geometry_area"], on="iso3")
