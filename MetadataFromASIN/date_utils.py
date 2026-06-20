"""
Utility helpers for parsing publication date strings into timezone-aware
``datetime`` objects recognized by Calibre.
"""
from __future__ import annotations
import datetime as _dt
import re
from typing import Optional

from .calibre_compat import parse_only_date, utc_tz

_JP_DATE = re.compile(r"(\d{4})\u5e74\s*(\d{1,2})\u6708\s*(\d{1,2})\u65e5")  # YYYY[year]MM[month]DD[day]
_ISO_DATE = re.compile(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})")

def _to_utc(y: int, m: int = 1, d: int = 1) -> _dt.datetime:
    return _dt.datetime(y, m, d, tzinfo=utc_tz)

def _try_patterns(text: str) -> Optional[_dt.datetime]:
    for pat in (_JP_DATE, _ISO_DATE):
        if m := pat.search(text):
            y, mm, dd = map(int, m.groups())
            return _to_utc(y, mm, dd)
    return None

def parse_pubdate(text: str) -> Optional[_dt.datetime]:
    """
    Convert various Japanese/ISO date notations into timezone-aware
    :class:`datetime.datetime` objects (UTC).
    """
    if dt := _try_patterns(text):
        return dt
    try:
        maybe = parse_only_date(text)
        if isinstance(maybe, _dt.date):
            return _to_utc(maybe.year, maybe.month, maybe.day)
    except Exception:
        pass
    return None
