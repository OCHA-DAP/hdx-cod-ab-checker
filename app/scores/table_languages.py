from pandas import DataFrame

from ..config import romanized_languages


def main(checks: DataFrame) -> DataFrame:
    """Score languages used within dataset.

    Gives a perfect score if at least 1 language column is detected and all language
    codes are valid.
    """
    scores = checks[["iso3", "version", "level"]].copy()
    scores["language_exists"] = checks["language_count"].ge(1)
    scores["language_valid"] = checks["language_invalid"].eq(0)
    scores["language_romanized"] = checks["language_1"].isin(romanized_languages)
    scores["language_hierarchy"] = checks["language_parent"].isna() | checks[
        "language_count"
    ].le(checks["language_parent"])
    return scores
