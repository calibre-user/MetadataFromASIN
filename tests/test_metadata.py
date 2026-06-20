"""Tests for the metadata orchestration layer with a stubbed fetcher."""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.calibre_compat import Metadata  # noqa: E402
from MetadataFromASIN.metadata import (  # noqa: E402
    DEFAULT_SRU_FLAGS,
    apply_sru_to_metadata,
    get_metadata_from_asin,
)

_FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load(name):
    with open(os.path.join(_FIXTURES, name), encoding="utf-8") as handle:
        return handle.read()


class _Log:
    def info(self, msg):
        pass

    def debug(self, msg):
        pass

    def error(self, msg):
        pass


_AMAZON_HTML = (
    "<html><body>"
    '<a href="/dp/4101001014">product</a>'
    '<div id="bookDescription_feature_div"><p>Hello description</p></div>'
    "</body></html>"
)


class GetMetadataFromAsinTests(unittest.TestCase):
    def setUp(self):
        self.sru_xml = _load("ndl_sample.xml")
        self.requested_urls = []

    def _fake_fetch(self, url, log, timeout):
        self.requested_urls.append(url)
        if "ndlsearch" in url:
            return self.sru_xml
        return _AMAZON_HTML

    def test_combines_amazon_and_sru(self):
        mi = get_metadata_from_asin(
            "4101001014", "co.jp", _Log(), 30, self._fake_fetch
        )
        self.assertIsNotNone(mi)
        self.assertEqual(mi.isbn, "9784101001012")
        self.assertEqual(mi.identifiers["isbn10"], "4101001014")
        self.assertEqual(mi.identifiers["isbn13"], "9784101001012")
        # Enriched from the NDL SRU fixture.
        self.assertEqual(mi.title, "Test Title (My Series)")
        self.assertEqual(mi.authors, ["Yamada Taro 1950-"])
        self.assertEqual(mi.publisher, "Test Publisher")
        self.assertEqual(mi.language, "jpn")
        self.assertEqual(
            mi.pubdate, datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
        )

    def test_queries_amazon_then_ndl(self):
        get_metadata_from_asin("4101001014", "co.jp", _Log(), 30, self._fake_fetch)
        self.assertEqual(len(self.requested_urls), 2)
        self.assertIn("amazon.co.jp", self.requested_urls[0])
        self.assertIn("ndlsearch", self.requested_urls[1])

    def test_returns_none_when_amazon_fetch_empty(self):
        mi = get_metadata_from_asin(
            "4101001014", "co.jp", _Log(), 30, lambda url, log, timeout: ""
        )
        self.assertIsNone(mi)

    def test_sru_skipped_when_all_flags_disabled(self):
        mi = get_metadata_from_asin(
            "4101001014", "co.jp", _Log(), 30, self._fake_fetch, sru_flags={}
        )
        self.assertIsNotNone(mi)
        # Only the Amazon page is fetched when SRU is fully disabled.
        self.assertEqual(len(self.requested_urls), 1)
        self.assertEqual(mi.title, "")


class ApplySruToMetadataTests(unittest.TestCase):
    def _sru(self):
        return {
            "title": "T",
            "sort_title": "T (S)",
            "series": "S",
            "series_index": 2,
            "authors": ["A"],
            "author_sort": "A sort",
            "publisher": "P",
            "language": "jpn",
            "pubdate": datetime.datetime(2022, 6, 1, tzinfo=datetime.timezone.utc),
        }

    def test_full_mapping(self):
        mi = Metadata("", [])
        pubdate = apply_sru_to_metadata(mi, self._sru(), dict(DEFAULT_SRU_FLAGS))
        self.assertEqual(mi.title, "T")
        self.assertEqual(mi.title_sort, "T (S)")
        self.assertEqual(mi.series, "S")
        self.assertEqual(mi.series_index, 2)
        self.assertEqual(mi.authors, ["A"])
        self.assertEqual(mi.author_sort, "A sort")
        self.assertEqual(mi.publisher, "P")
        self.assertEqual(mi.language, "jpn")
        self.assertEqual(
            pubdate, datetime.datetime(2022, 6, 1, tzinfo=datetime.timezone.utc)
        )

    def test_existing_pubdate_takes_priority(self):
        mi = Metadata("", [])
        existing = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
        pubdate = apply_sru_to_metadata(
            mi, self._sru(), dict(DEFAULT_SRU_FLAGS), existing
        )
        self.assertEqual(pubdate, existing)

    def test_disabled_flags_leave_fields_untouched(self):
        mi = Metadata("", [])
        flags = {key: False for key in DEFAULT_SRU_FLAGS}
        apply_sru_to_metadata(mi, self._sru(), flags)
        self.assertEqual(mi.title, "")
        self.assertEqual(mi.authors, [])
        self.assertEqual(mi.publisher, "")


if __name__ == "__main__":
    unittest.main()
