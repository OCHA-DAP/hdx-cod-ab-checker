from pandas import DataFrame

from ..config import EPSG_WGS84


def main(checks: DataFrame) -> DataFrame:
    """Create scores based on valid geometry."""
    scores = checks[["iso3", "version", "level"]].copy()
    scores["geom_count"] = checks["level"].eq(0) & checks["geom_count"].eq(1) | checks[
        "level"
    ].gt(0) & checks["geom_count"].gt(0)
    scores["geom_not_empty"] = checks["geom_empty"].eq(0)
    scores["geom_2d"] = checks["geom_has_z"].eq(0)
    scores["geom_valid"] = checks["geom_invalid"].eq(0)
    scores["geom_proj_wgs84"] = checks["geom_proj"].eq(EPSG_WGS84)
    scores["geom_bbox_valid"] = (
        checks["geom_min_x"].ge(-180)
        & checks["geom_min_y"].ge(-90)
        & checks["geom_max_x"].le(180)
        & checks["geom_max_y"].le(90)
    )
    return scores
