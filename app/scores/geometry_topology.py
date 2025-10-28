from pandas import DataFrame

from ..config import SLIVER_GAP_AREA_KM, SLIVER_GAP_THINNESS


def main(checks: DataFrame) -> DataFrame:
    """Create scores based on geometry topology."""
    scores = checks[["iso3", "version", "level"]].copy()
    scores["geom_no_gaps"] = (
        checks["geom_gap_area_km"].isna()
        | checks["geom_gap_area_km"].gt(SLIVER_GAP_AREA_KM)
        | checks["geom_gap_thinness"].isna()
        | checks["geom_gap_thinness"].gt(SLIVER_GAP_THINNESS)
    )
    scores["geom_no_overlaps"] = checks["geom_overlaps_self"].eq(0)
    scores["geom_within_parent"] = checks["geom_not_within_parent"].eq(0)
    scores["geom_within_pcode"] = checks["geom_not_within_pcode"].isna() | checks[
        "geom_not_within_pcode"
    ].eq(0)
    return scores
