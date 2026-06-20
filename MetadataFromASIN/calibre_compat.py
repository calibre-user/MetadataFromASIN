from __future__ import annotations

import datetime as _dt
import html as _html
import random
import re
import urllib.request
from html.parser import HTMLParser as _HTMLParser
from urllib.parse import urlparse as _urlparse
from dataclasses import dataclass
from typing import Any, Optional

try:
    from calibre import browser, random_user_agent, xml_replace_entities
    from calibre.ebooks.metadata import check_isbn
    from calibre.ebooks.metadata.book.base import Metadata
    from calibre.ebooks.metadata.sources.base import Option, Source
    from calibre.library.comments import sanitize_comments_html
    from calibre.utils.date import parse_only_date, utc_tz

    CALIBRE_AVAILABLE = True
except ImportError:
    CALIBRE_AVAILABLE = False
    utc_tz = _dt.timezone.utc

    _USER_AGENTS = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    )

    @dataclass(frozen=True)
    class Option:
        name: str
        type: str
        default: Any
        label: str
        desc: str
        choices: Optional[tuple[Any, ...]] = None

    class _Prefs:
        def __init__(self, values: Optional[dict[str, Any]] = None):
            self._values = dict(values or {})

        def get(self, key: str, default: Any = None) -> Any:
            return self._values.get(key, default)

        def set(self, key: str, value: Any) -> None:
            self._values[key] = value

    class Source:
        def __init__(self, *args: Any, **kwargs: Any):
            options = getattr(self, "options", ())
            self.prefs = _Prefs({opt.name: opt.default for opt in options})

    class Metadata:
        def __init__(self, title: str, authors: list[str]):
            self.title = title
            self.authors = authors
            self.identifiers: dict[str, str] = {}
            self.isbn = ""
            self.title_sort = ""
            self.author_sort = ""
            self.series = ""
            self.series_index = 1
            self.tags: Optional[list[str]] = None
            self.rating: Optional[float] = None
            self.comments = ""
            self.pubdate: Optional[_dt.datetime] = None
            self.publisher = ""
            self.language = ""

        def __repr__(self) -> str:
            parts = [
                f"title={self.title!r}",
                f"authors={self.authors!r}",
                f"identifiers={self.identifiers!r}",
            ]
            for name in (
                "isbn",
                "title_sort",
                "author_sort",
                "series",
                "series_index",
                "tags",
                "rating",
                "publisher",
                "language",
                "pubdate",
            ):
                value = getattr(self, name, None)
                if value:
                    parts.append(f"{name}={value!r}")
            if self.comments:
                parts.append(f"comments={self.comments!r}")
            return f"Metadata({', '.join(parts)})"

    class _StandaloneBrowser:
        def __init__(self):
            self.addheaders: list[tuple[str, str]] = []

        def open(self, url: str, timeout: int = 30):
            headers = dict(self.addheaders)
            headers.setdefault("User-Agent", random_user_agent())
            headers.setdefault(
                "Accept",
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            )
            headers.setdefault("Accept-Language", "ja,en-US;q=0.8,en;q=0.6")
            request = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(request, timeout=timeout)

    def browser() -> _StandaloneBrowser:
        return _StandaloneBrowser()

    def random_user_agent() -> str:
        return random.choice(_USER_AGENTS)

    def xml_replace_entities(raw: str, encoding: str = "utf-8") -> str:
        return _html.unescape(raw)

    class _CommentHTMLSanitizer(_HTMLParser):
        _ALLOWED_TAGS = {
            "a",
            "b",
            "blockquote",
            "br",
            "div",
            "em",
            "i",
            "li",
            "ol",
            "p",
            "span",
            "strong",
            "ul",
        }
        _VOID_TAGS = {"br"}
        _GLOBAL_ATTRS = {"title"}
        _TAG_ATTRS = {"a": {"href", "name", "title"}}
        _SAFE_SCHEMES = {"", "http", "https", "mailto"}

        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts: list[str] = []

        def _clean_attrs(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> list[tuple[str, str]]:
            allowed = self._GLOBAL_ATTRS | self._TAG_ATTRS.get(tag, set())
            cleaned = []
            for name, value in attrs:
                name = name.lower()
                if name not in allowed or value is None:
                    continue
                cleaned_value = value
                if name == "href":
                    cleaned_value = value.strip()
                    if _urlparse(cleaned_value).scheme.lower() not in self._SAFE_SCHEMES:
                        continue
                cleaned.append((name, cleaned_value))
            return cleaned

        @staticmethod
        def _render_attrs(attrs: list[tuple[str, str]]) -> str:
            if not attrs:
                return ""
            rendered = (
                f'{name}="{_html.escape(value, quote=True)}"'
                for name, value in attrs
            )
            return " " + " ".join(rendered)

        def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
            tag = tag.lower()
            if tag not in self._ALLOWED_TAGS:
                return
            cleaned_attrs = self._clean_attrs(tag, attrs)
            self.parts.append(f"<{tag}{self._render_attrs(cleaned_attrs)}>")

        def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
            self.handle_starttag(tag, attrs)

        def handle_endtag(self, tag: str) -> None:
            tag = tag.lower()
            if tag in self._ALLOWED_TAGS and tag not in self._VOID_TAGS:
                self.parts.append(f"</{tag}>")

        def handle_data(self, data: str) -> None:
            self.parts.append(_html.escape(data))

        def handle_entityref(self, name: str) -> None:
            self.parts.append(f"&{name};")

        def handle_charref(self, name: str) -> None:
            self.parts.append(f"&#{name};")

        def html(self) -> str:
            return "".join(self.parts)

    def sanitize_comments_html(raw: str) -> str:
        raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", raw)
        sanitizer = _CommentHTMLSanitizer()
        sanitizer.feed(raw)
        return sanitizer.html()

    def check_isbn(isbn: str) -> Optional[str]:
        clean = isbn.upper().replace("-", "").replace(" ", "")
        if re.fullmatch(r"\d{9}[\dX]", clean):
            total = 0
            for index, char in enumerate(clean):
                value = 10 if char == "X" else int(char)
                total += (10 - index) * value
            return clean if total % 11 == 0 else None
        if re.fullmatch(r"\d{13}", clean):
            total = sum(
                int(char) if index % 2 == 0 else int(char) * 3
                for index, char in enumerate(clean)
            )
            return clean if total % 10 == 0 else None
        return None

    def parse_only_date(text: str) -> Optional[_dt.date]:
        patterns = (
            r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
            r"(\d{4})\u5e74\s*(\d{1,2})\u6708\s*(\d{1,2})\u65e5",  # YYYY[year]MM[month]DD[day]
            r"(\d{4})[/-](\d{1,2})",
            r"(\d{4})\u5e74\s*(\d{1,2})\u6708",  # YYYY[year]MM[month]
            r"(\d{4})",
        )
        for pattern in patterns:
            if match := re.search(pattern, text):
                nums = [int(part) for part in match.groups()]
                year = nums[0]
                month = nums[1] if len(nums) > 1 else 1
                day = nums[2] if len(nums) > 2 else 1
                try:
                    return _dt.date(year, month, day)
                except ValueError:
                    return None
        return None
