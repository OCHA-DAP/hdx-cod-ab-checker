from pandas import DataFrame, read_parquet

from ..config import data_dir, m49_df
from . import (
    geometry_areas,
    geometry_topology,
    geometry_validity,
    table_areas,
    table_dates,
    table_languages,
    table_names,
    table_other,
    table_pcodes,
)


def aggregate(checks: DataFrame) -> DataFrame:
    """Summarize scores by averaging scores from each admin level."""
    checks = checks.drop(columns=["level"])
    checks = checks.groupby(["iso3", "version"], dropna=False).mean()
    checks["score"] = checks.mean(axis=1)
    checks = checks.round(3)
    return checks.reset_index()


def output_scores(checks: DataFrame) -> None:
    """Aggregate scores and outputs to an Excel workbook with highlight coloring."""
    scores = aggregate(checks)
    names = m49_df[["en_short", "iso3"]].rename(columns={"en_short": "name"})
    scores = names.merge(scores, on="iso3")
    scores = scores.sort_values(by=["iso3", "version"])
    scores.to_parquet(data_dir / "scores.parquet", compression="zstd")
    scores.to_csv(data_dir / "scores.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    """Apply scoring to the summarized values in "checks.csv"."""
    # NOTE: Register scores here.
    score_functions = (
        geometry_validity,
        geometry_topology,
        geometry_areas,
        table_pcodes,
        table_names,
        table_languages,
        table_dates,
        table_areas,
        table_other,
    )

    checks = read_parquet(data_dir / "checks.parquet")
    score_results = []
    for function in score_functions:
        partial = function.main(checks)
        score_results.append(partial)
    output_table = None
    for partial in score_results:
        if output_table is None:
            output_table = partial
        else:
            output_table = output_table.merge(
                partial,
                on=["iso3", "version", "level"],
                how="outer",
            )
    if output_table is not None:
        output_scores(output_table)
