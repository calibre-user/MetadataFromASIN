from __future__ import annotations
"""Shared constants and selector definitions used across the plugin."""

import re
from typing import Final, Pattern, Tuple, Dict

# -----------------------------------------------------------------
# ISBN
# -----------------------------------------------------------------
ISBN10_REGEX: Final[Pattern[str]] = re.compile(r"^[0-9]{9}[0-9X]$")
ISBN13_REGEX: Final[Pattern[str]] = re.compile(r"^[0-9]{13}$")

# -----------------------------------------------------------------
# Amazon definitions
# -----------------------------------------------------------------
AMAZON_DOMAINS: Final[Tuple[str, ...]] = (
    "com", "co.uk", "de", "fr", "co.jp", "it", "es",
    "com.au", "ca", "com.mx", "com.br", "nl", "se",
    "com.tr", "ae", "sa", "eg", "sg", "in", "co.kr",
    "co.id", "co.th", "com.tw",
)

class AMZPaths:
    VARIANT_IDS: Final[Tuple[str, ...]] = ("OTHER", "PAPERBACK", "HARDCOVER")
    BREADCRUMB_DIV: Final[str] = "wayfinding-breadcrumbs_feature_div"
    DESC_DIVS: Final[Tuple[str, ...]] = (
        "drengr_MobileTabbedDescriptionOverviewContent_feature_div",
        "drengr_DesktopTabbedDescriptionOverviewContent_feature_div",
        "bookDescription_feature_div",
        "productDescription",
    )
    RATING_SPAN_ID: Final[str]   = "acrPopover"
    RATING_ICON_CLASS: Final[str] = "a-icon-alt"
    SLUG_REGEX: Final[Pattern[str]] = re.compile(r"/dp/([0-9X]{10}|[0-9]{13})")

# -----------------------------------------------------------------
# NDL SRU definitions
# -----------------------------------------------------------------
SRU_NS: Final[Dict[str, str]] = {
    "srw":    "http://www.loc.gov/zing/srw/",
    "rdf":    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dc":     "http://purl.org/dc/elements/1.1/",
    "dcterms":"http://purl.org/dc/terms/",
    "dcndl":  "http://ndl.go.jp/dcndl/terms/",
    "foaf":   "http://xmlns.com/foaf/0.1/",
}
class SRUPaths:
    TITLE_VAL   = "dc:title/rdf:Description/rdf:value/text()"
    TITLE_TR    = "dc:title/rdf:Description/dcndl:transcription/text()"
    SERIES_VAL  = "dcndl:seriesTitle/rdf:Description/rdf:value/text()"
    SERIES_TR   = "dcndl:seriesTitle/rdf:Description/dcndl:transcription/text()"
    VOLUME_VAL  = "dcndl:volume/rdf:Description/rdf:value/text()"
    VOLUME_TR   = "dcndl:volume/rdf:Description/dcndl:transcription/text()"
    CREATORS      = "dcterms:creator"
    CREATOR_NAME  = "foaf:Agent/foaf:name/text()"
    CREATOR_TRANS = "foaf:Agent/dcndl:transcription/text()"
