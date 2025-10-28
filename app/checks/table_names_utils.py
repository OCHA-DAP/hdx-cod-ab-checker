from icu import (
    USET_ADD_CASE_MAPPINGS,  # pyright: ignore[reportAttributeAccessIssue]
    LocaleData,  # pyright: ignore[reportAttributeAccessIssue]
    ULocaleDataExemplarSetType,  # pyright: ignore[reportAttributeAccessIssue]
)
from langcodes import tag_is_valid

from ..config import m49, official_languages
from .table_names_config import auxiliary_codes, exclude_check, punctuation_set


def get_char_set(lang: str, iso3: str) -> list[str]:
    """Get character set for a language code."""
    return [
        x
        for y in LocaleData(lang).getExemplarSet(
            USET_ADD_CASE_MAPPINGS,
            ULocaleDataExemplarSetType.ES_STANDARD,
        )
        for x in y
    ] + [chr(int(x[2:], 16)) for x in auxiliary_codes.get(f"{lang}-{iso3}", [])]  # noqa: FURB166


def get_invalid_chars(lang: str, name: str | None, iso3: str) -> str:
    """Check if a value within a column is a valid name based on it's language code."""
    if not name or not name.strip() or not tag_is_valid(lang) or lang in exclude_check:
        return ""
    char_set = get_char_set(lang, iso3)
    return "".join({char for char in name if char not in char_set + punctuation_set})


def is_invalid_adm0(lang: str, name: str | None, iso3: str) -> bool:
    """Check if Admin 0 name is invalid."""
    if lang not in official_languages:
        return False
    if iso3 in m49:
        return name != m49[iso3][f"{lang}_short"]
    return False


def is_upper(name: str | None) -> bool:
    """Check if name is all uppercase."""
    if not name or not name.strip():
        return False
    return name == name.upper() and name.lower() != name.upper()


def is_lower(name: str | None) -> bool:
    """Check if name is all lowercase."""
    if not name or not name.strip():
        return False
    return name == name.lower() and name.lower() != name.upper()


def is_punctuation(lang: str, name: str | None, iso3: str) -> bool:
    """Check if a value within a column is a valid name based on it's language code."""
    if not name or not name.strip() or not tag_is_valid(lang):
        return False
    char_set = get_char_set(lang, iso3)
    return all(char not in char_set for char in name)


def is_invalid(lang: str, name: str | None, iso3: str) -> bool:
    """Check if a value within a column is a valid name based on it's language code."""
    if not name or not name.strip() or not tag_is_valid(lang) or lang in exclude_check:
        return False
    char_set = get_char_set(lang, iso3)
    return any(char not in char_set + punctuation_set for char in name)


def has_double_spaces(name: str | None) -> bool:
    """Check if string has double spaces."""
    if not name or not name.strip():
        return False
    return "  " in name


def has_strippable_spaces(name: str | None) -> bool:
    """Check if string has strippable spaces."""
    if not name or not name.strip():
        return False
    return name != name.strip()
