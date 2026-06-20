"""String normalization helpers."""

import re

__all__ = ["clean_commas", "normalize_sep"]

# Matches ";" (U+003B) and the full-width ";" (U+FF1B) surrounded by spaces.
_SEP_PAT = re.compile(r"\s*[;\uFF1B]\s*")
_COMMA_PAT = re.compile(r"\s*,\s*")
_WS_PAT = re.compile(r"\s+")


def normalize_sep(s: str) -> str:
    """Unify ";"/full-width ";" separators to " : " and trim surrounding space."""
    return _SEP_PAT.sub(" : ", s).strip()


def clean_commas(s: str) -> str:
    """Turn "Last, First" style commas into spaces and collapse repeated spaces."""
    return _WS_PAT.sub(" ", _COMMA_PAT.sub(" ", s)).strip()
