"""
URL utility functions for Amazon product pages and NDL SRU queries.
"""
from typing import Final

_AMAZON_BASE: Final[str] = "https://www.amazon.{domain}"
_AMAZON_PRODUCT: Final[str] = "/dp/{asin}"

_SRU_TEMPLATE: Final[str] = (
    "https://ndlsearch.ndl.go.jp/api/sru?operation=searchRetrieve"
    "&version=1.2&recordSchema=dcndl&recordPacking=xml&onlyBib=true"
    "&query=isbn={isbn}"
)


def amazon_product_url(asin: str, domain: str) -> str:
    """
    Build Amazon product-page URL for a given ASIN and domain.
    """
    return _AMAZON_BASE.format(domain=domain) + _AMAZON_PRODUCT.format(asin=asin)


def ndl_sru_url(isbn: str) -> str:
    """
    Build SRU query URL for National Diet Library searches by ISBN.
    """
    return _SRU_TEMPLATE.format(isbn=isbn)
