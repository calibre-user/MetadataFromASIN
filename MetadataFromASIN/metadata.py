from __future__ import annotations
"""Combine Amazon and NDL SRU data into a Calibre ``Metadata`` object.

Supports optional pubdate / publisher / language enrichment.
"""

import datetime
import re
from typing import Callable, Dict, Optional

from .amazon_parser import parse_amazon_page
from .calibre_compat import Metadata
from .date_utils import parse_pubdate
from .fetcher import fetch_page
from .ndl_sru_parser import parse_sru
from .urls import amazon_product_url, ndl_sru_url

__all__ = ("DEFAULT_SRU_FLAGS", "apply_sru_to_metadata", "get_metadata_from_asin")

# All SRU enrichment fields enabled.
DEFAULT_SRU_FLAGS: Dict[str, bool] = dict(
    title=True,
    title_reading=True,
    series=True,
    series_reading=True,
    authors=True,
    author_reading=True,
    publisher=True,
    language=True,
    pubdate=True,
)

# "\u767a\u58f2\u65e5" == Japanese for "release date".
_PUBDATE_LABEL = re.compile(r"(\u767a\u58f2\u65e5|Publication date)")
_LIST_ITEM = re.compile(r"<li[^>]*>(.*?)</li>", re.S)
_HTML_TAG = re.compile(r"<[^>]+>")


def _amazon_pubdate(html: str) -> Optional[datetime.datetime]:
    """Extract the publication date from an Amazon product page, if present."""
    for item in _LIST_ITEM.findall(html):
        if _PUBDATE_LABEL.search(item):
            return parse_pubdate(_HTML_TAG.sub("", item))
    return None


def apply_sru_to_metadata(
    mi: Metadata,
    sru: Dict,
    sru_flags: Dict[str, bool],
    existing_pubdate: Optional[datetime.datetime] = None,
) -> Optional[datetime.datetime]:
    """Map a parsed SRU record onto ``mi`` according to ``sru_flags``.

    Returns the resolved publication date (``existing_pubdate`` takes priority
    over the SRU value).
    """
    if sru_flags.get("title"):
        mi.title = sru["title"]
    if sru_flags.get("title_reading"):
        mi.title_sort = sru["sort_title"]

    if sru_flags.get("series"):
        mi.series = sru["series"]
        mi.series_index = int(sru["series_index"])
    if not sru_flags.get("series_reading") and sru_flags.get("title_reading"):
        mi.title_sort = mi.title_sort.split(" (")[0]

    if sru_flags.get("authors"):
        mi.authors = sru["authors"]
    if sru_flags.get("author_reading"):
        mi.author_sort = sru["author_sort"]

    if sru_flags.get("publisher") and sru.get("publisher"):
        mi.publisher = sru["publisher"]
    if sru_flags.get("language") and sru.get("language"):
        mi.language = sru["language"]

    pubdate = existing_pubdate
    if not pubdate and sru_flags.get("pubdate") and sru.get("pubdate"):
        pubdate = sru["pubdate"]
    return pubdate


def get_metadata_from_asin(
    asin: str,
    domain: str,
    log,
    timeout: int,
    fetch_page_func: Callable[[str, object, int], str] = fetch_page,
    *,
    include_tags: bool = True,
    include_rating: bool = True,
    include_comments: bool = True,
    sru_flags: Optional[Dict[str, bool]] = None,
) -> Optional[Metadata]:
    """Build a ``Metadata`` object from an Amazon ASIN, enriched via NDL SRU."""
    if sru_flags is None:
        sru_flags = dict(DEFAULT_SRU_FLAGS)

    # ---------- Amazon ----------------------------------------------
    html = fetch_page_func(amazon_product_url(asin, domain), log, timeout)
    if not html:
        return None
    ainfo = parse_amazon_page(html, log)

    mi = Metadata("", [])
    if ainfo["isbn10"]:
        mi.identifiers["isbn10"] = ainfo["isbn10"]
    if ainfo["isbn13"]:
        mi.identifiers["isbn13"] = ainfo["isbn13"]
        mi.isbn = ainfo["isbn13"]
    else:
        mi.isbn = ainfo["isbn10"]

    if include_tags and ainfo["tags"]:
        mi.tags = ainfo["tags"]

    # Rating is clamped to the 0-5 range expected by Calibre.
    if include_rating and ainfo["rating"] is not None:
        mi.rating = max(0, min(5, ainfo["rating"]))

    if include_comments and ainfo["comments"]:
        mi.comments = ainfo["comments"]

    pubdate = _amazon_pubdate(html)

    # ---------- NDL SRU ---------------------------------------------
    if mi.isbn and any(sru_flags.values()):
        xml = fetch_page_func(ndl_sru_url(mi.isbn), log, timeout)
        if xml:
            sru = parse_sru(xml)
            # Amazon's pubdate wins; fall back to the SRU value otherwise.
            pubdate = apply_sru_to_metadata(mi, sru, sru_flags, pubdate)

    if pubdate:
        mi.pubdate = pubdate

    return mi
