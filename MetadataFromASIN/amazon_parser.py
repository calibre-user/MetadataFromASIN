from __future__ import annotations
"""Amazon product-page parser.

Extracts ISBN, breadcrumb tags, rating and the product description.
"""

import re
from html import escape
from html.parser import HTMLParser
from typing import Any, Dict, Final, List, Optional
from urllib.parse import unquote

from .calibre_compat import sanitize_comments_html, xml_replace_entities
from .config import AMZPaths
from .isbn_utils import (
    convert_isbn10_to_isbn13,
    normalize_isbn10,
    normalize_isbn13,
)

__all__: Final[tuple[str, ...]] = ("parse_amazon_page",)


class _AmazonHTMLParser(HTMLParser):
    _CONTENT_TAGS = {"p", "br", "ul", "ol", "li", "b", "strong", "i", "em", "a"}
    _VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []
        self.variant_hrefs: list[str] = []
        self.rating_titles: list[str] = []
        self.rating_texts: list[str] = []
        self.breadcrumb_text: list[str] = []
        self.description_chunks: list[str] = []
        self._variant_depth = 0
        self._breadcrumb_depth = 0
        self._rating_depth = 0
        self._description_container_depth = 0
        self._description_content_depth = 0
        self._expander_header_depth = 0

    @staticmethod
    def _attrs(attrs: list[tuple[str, Optional[str]]]) -> dict[str, str]:
        return {name.lower(): value or "" for name, value in attrs}

    @staticmethod
    def _start_tag(tag: str, attrs: list[tuple[str, Optional[str]]]) -> str:
        rendered = []
        for name, value in attrs:
            if value is None:
                rendered.append(name)
            else:
                rendered.append(f'{name}="{escape(value, quote=True)}"')
        return f"<{tag}{(' ' + ' '.join(rendered)) if rendered else ''}>"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        is_void = tag in self._VOID_TAGS
        attrs_dict = self._attrs(attrs)
        elem_id = attrs_dict.get("id", "")
        classes = attrs_dict.get("class", "").split()

        starts_description = elem_id in AMZPaths.DESC_DIVS
        if (starts_description or self._description_container_depth) and not is_void:
            self._description_container_depth += 1

        if not is_void and (
            self._expander_header_depth
            or ("a-expander-header" in classes and self._description_container_depth)
        ):
            self._expander_header_depth += 1

        starts_description_content = starts_description
        if starts_description_content or self._description_content_depth:
            if tag in self._CONTENT_TAGS and not self._expander_header_depth:
                self.description_chunks.append(self._start_tag(tag, attrs))
            if not is_void:
                self._description_content_depth += 1

        if self._variant_depth or elem_id in {
            f"tmm-grid-swatch-{fmt}" for fmt in AMZPaths.VARIANT_IDS
        }:
            if not is_void:
                self._variant_depth += 1

        if self._breadcrumb_depth or elem_id == AMZPaths.BREADCRUMB_DIV:
            if not is_void:
                self._breadcrumb_depth += 1

        if tag == "span" and elem_id == AMZPaths.RATING_SPAN_ID and attrs_dict.get("title"):
            self.rating_titles.append(attrs_dict["title"])

        if self._rating_depth or AMZPaths.RATING_ICON_CLASS in classes:
            if not is_void:
                self._rating_depth += 1

        href = attrs_dict.get("href")
        if href:
            self.hrefs.append(href)
            if self._variant_depth:
                self.variant_hrefs.append(href)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if self._description_content_depth and tag in self._CONTENT_TAGS and not self._expander_header_depth:
            self.description_chunks.append(self._start_tag(tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._VOID_TAGS:
            return
        if self._description_content_depth:
            if tag in self._CONTENT_TAGS and not self._expander_header_depth:
                self.description_chunks.append(f"</{tag}>")
            self._description_content_depth -= 1
        if self._description_container_depth:
            self._description_container_depth -= 1
        if self._expander_header_depth:
            self._expander_header_depth -= 1
        if self._variant_depth:
            self._variant_depth -= 1
        if self._breadcrumb_depth:
            self._breadcrumb_depth -= 1
        if self._rating_depth:
            self._rating_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._description_content_depth and not self._expander_header_depth:
            self.description_chunks.append(escape(data))
        if self._breadcrumb_depth:
            self.breadcrumb_text.append(data)
        if self._rating_depth:
            self.rating_texts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._description_content_depth and not self._expander_header_depth:
            self.description_chunks.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._description_content_depth and not self._expander_header_depth:
            self.description_chunks.append(f"&#{name};")


def _rating_from_strings(values: list[str]) -> Optional[float]:
    for value in values:
        if match := re.search(r"(\d+(?:[.,]\d+))", value):
            return float(match.group(1).replace(",", "."))
    return None


def _extract_slug_from_hrefs(hrefs: list[str]) -> Optional[str]:
    for href in hrefs:
        if match := AMZPaths.SLUG_REGEX.search(unquote(href)):
            return match.group(1)
    return None


def _clean_comments(raw: str) -> str:
    raw = re.sub(
        r"""(?is)<p\b[^>]*>\s*<a\b[^>]*href\s*=\s*(['"])javascript:void\(0\)\1[^>]*>.*?</a>\s*</p>""",
        "",
        raw,
    )
    raw = re.sub(
        r"""(?is)<a\b[^>]*href\s*=\s*(['"])javascript:void\(0\)\1[^>]*>.*?</a>""",
        "",
        raw,
    )
    cleaned = sanitize_comments_html(xml_replace_entities(raw, "utf-8"))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"(?:<br\s*/?>\s*)+$", "", cleaned).strip()
    return cleaned


def _parse_tags(text: str) -> Optional[List[str]]:
    # Amazon breadcrumbs are separated by "\u203a" (single right angle quote).
    tags = [part.strip() for part in text.split("\u203a") if part.strip()]
    return tags or None


def parse_amazon_page(html: str, log) -> Dict[str, Any]:
    """Parse Amazon product-page HTML into a dict."""
    parser = _AmazonHTMLParser()
    parser.feed(html)

    slug = (
        _extract_slug_from_hrefs(parser.variant_hrefs)
        or _extract_slug_from_hrefs(parser.hrefs)
    )
    if not slug:
        raise ValueError("Failed to extract ISBN/ASIN slug")

    isbn10 = normalize_isbn10(slug)
    isbn13 = isbn10 and convert_isbn10_to_isbn13(isbn10) or normalize_isbn13(slug)
    if not (isbn10 or isbn13):
        raise ValueError("Slug is not a valid ISBN")

    return {
        "isbn10": isbn10,
        "isbn13": isbn13,
        "tags": _parse_tags(" ".join(parser.breadcrumb_text)),
        "rating": _rating_from_strings(parser.rating_titles + parser.rating_texts),
        "comments": _clean_comments("".join(parser.description_chunks))
        if parser.description_chunks
        else "",
    }
