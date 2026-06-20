from __future__ import annotations
"""NDL SRU response parser.

- De-duplicates authors (entries carrying date ranges are preferred).
- Extracts publisher / language / pubdate.
- Prefers a BibResource that carries series elements.
"""

import re
import datetime
from typing import Dict, OrderedDict
from collections import OrderedDict as OD
from xml.etree import ElementTree as ET

from .calibre_compat import utc_tz
from .config import SRU_NS, SRUPaths
from .text_utils import clean_commas, normalize_sep

__all__ = ("parse_sru",)

# ------------------------------------------------------------------
# Normalization helpers
# Trailing " YYYY" or " YYYY-YYYY" date range appended to a name.
_DATE_PAT = re.compile(r"\s+\d{4}(?:-\d{4})?[-]?$")
# Whitespace, commas, periods and the ideographic space (U+3000).
_CAN_PAT = re.compile(r"[ ,.\u3000]+")
# Multiplication sign: times sign (U+00D7).
_X_PAT = re.compile(r"[\u00D7]")
# Full-width comma (U+FF0C).
_FULLWIDTH_COMMA = "\uFF0C"


def _canon_name(disp: str) -> str:
    base = _DATE_PAT.sub("", disp).strip()
    # Detect CJK characters (Hiragana/Katakana U+3040-30FF, Kanji U+4E00-9FFF).
    if re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", base):
        tmp = _X_PAT.sub(" ", base).replace("\u3000", " ")
        tmp = tmp.replace(",", "").replace(_FULLWIDTH_COMMA, "")
        canon = tmp.replace(" ", "")
    else:
        canon = _CAN_PAT.sub(" ", base).strip()
    return canon.lower()


def _choose_resource(resources):
    for r in resources:
        if r.find('.//dcndl:seriesTitle', SRU_NS) is not None:
            return r
    return resources[0]


def _to_utc(y: int, m: int = 1, d: int = 1) -> datetime.datetime:
    return datetime.datetime(y, m, d, tzinfo=utc_tz)


def _texts(elem: ET.Element, path: str) -> list[str]:
    suffix = "/text()"
    if path.endswith(suffix):
        path = path[:-len(suffix)]
    texts = []
    for found in elem.findall(path, SRU_NS):
        text = (found.text or "").strip()
        if text:
            texts.append(text)
    return texts


# ------------------------------------------------------------------
def parse_sru(xml: str) -> Dict:
    tree = ET.fromstring(xml.encode("utf-8"))

    # ISSUED_DATE (extraResponseData)
    issued_year = None
    facets = tree.find(".//srw:extraResponseData", SRU_NS)
    if facets is not None:
        lst = facets.find('.//lst[@name="ISSUED_DATE"]/int[@name]')
        if lst is not None:
            issued_year = lst.get("name")

    # BibResource elements
    resources = (
        tree.findall(".//srw:recordData/rdf:RDF/dcndl:BibResource", SRU_NS)
        or tree.findall(".//dcndl:BibResource", SRU_NS)
    )
    if not resources:
        raise ValueError("No BibResource found")

    tgt = _choose_resource(resources)

    # ---- Title / series
    tit = " : ".join(dict.fromkeys(
        normalize_sep(t) for t in _texts(tgt, SRUPaths.TITLE_VAL)
    ))
    titr = " : ".join(dict.fromkeys(
        normalize_sep(t) for t in _texts(tgt, SRUPaths.TITLE_TR)
    ))
    ser  = clean_commas(normalize_sep(
        (_texts(tgt, SRUPaths.SERIES_VAL) or [""])[0]
    ))
    serr = clean_commas(normalize_sep(
        (_texts(tgt, SRUPaths.SERIES_TR) or [""])[0]
    ))
    vol  = (_texts(tgt, SRUPaths.VOLUME_VAL) or [""])[0]
    volr = (_texts(tgt, SRUPaths.VOLUME_TR) or [""])[0]

    if vol:
        title = f"{tit} {vol} ({ser})"
        sort  = f"{titr} {volr} ({serr})" if titr else f"{volr} ({serr})"
        idx   = volr if volr else vol
    else:
        title = f"{tit} ({ser})"
        sort  = f"{titr} ({serr})" if titr else f"({serr})"
        idx   = 1

    series = f"{tit} ({ser})"

    # ---- Authors
    od: "OrderedDict[str, str]" = OD()
    sortd: Dict[str, str] = {}

    for r in resources:
        for c in r.findall(SRUPaths.CREATORS, SRU_NS):
            n = _texts(c, SRUPaths.CREATOR_NAME)
            if not n:
                continue
            disp = clean_commas(n[0])
            canon = _canon_name(disp)
            has_date = bool(_DATE_PAT.search(disp))

            # Prefer the variant that carries a date range.
            if canon not in od or (has_date and not _DATE_PAT.search(od[canon])):
                od[canon] = disp

            tr = _texts(c, SRUPaths.CREATOR_TRANS)
            sortd[disp] = clean_commas(tr[0]) if tr and tr[0].strip() else disp

    authors = list(od.values())

    # ---- publisher / language
    publisher = _texts(tgt, "dcterms:publisher/foaf:Agent/foaf:name/text()")
    publisher = publisher[0] if publisher else ""
    language = _texts(tgt, "dcterms:language/text()")
    language = language[0] if language else ""

    # ---- pubdate
    date_text = _texts(tgt, "dcterms:date/text()")
    date_text = date_text[0] if date_text else ""
    date_year = re.search(r"\d{4}", date_text)
    date_year = date_year.group() if date_year else None

    pubdate = None
    if date_text and issued_year and issued_year == date_year:
        nums = re.findall(r"\d+", date_text)
        y, m = int(nums[0]), int(nums[1]) if len(nums) > 1 else 1
        pubdate = _to_utc(y, m, 1)
    elif issued_year:
        pubdate = _to_utc(int(issued_year), 1, 1)

    return {
        "title": title,
        "sort_title": sort,
        "series": series,
        "series_index": idx,
        "authors": authors,
        "author_sort_map": {a: sortd.get(a, a) for a in authors},
        "author_sort": " & ".join(sortd.get(a, a) for a in authors),
        "publisher": publisher,
        "language": language,
        "pubdate": pubdate,
    }
