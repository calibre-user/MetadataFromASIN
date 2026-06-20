"""Tests for ndl_sru_parser.parse_sru using a synthetic SRU fixture."""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.ndl_sru_parser import parse_sru  # noqa: E402

_FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load(name):
    with open(os.path.join(_FIXTURES, name), encoding="utf-8") as handle:
        return handle.read()


class ParseSruTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = parse_sru(_load("ndl_sample.xml"))

    def test_title_includes_series(self):
        self.assertEqual(self.result["title"], "Test Title (My Series)")

    def test_sort_title_uses_transcription(self):
        self.assertEqual(
            self.result["sort_title"], "TEST TITLE READING (MY SERIES READING)"
        )

    def test_series_and_index(self):
        self.assertEqual(self.result["series"], "Test Title (My Series)")
        self.assertEqual(self.result["series_index"], 1)

    def test_authors_deduplicated_preferring_date_range(self):
        # The two creator entries collapse to one; the variant carrying the
        # "1950-" date range is preferred.
        self.assertEqual(self.result["authors"], ["Yamada Taro 1950-"])

    def test_author_sort_uses_transcription(self):
        self.assertEqual(self.result["author_sort"], "YAMADA TARO")

    def test_publisher_and_language(self):
        self.assertEqual(self.result["publisher"], "Test Publisher")
        self.assertEqual(self.result["language"], "jpn")

    def test_pubdate(self):
        self.assertEqual(
            self.result["pubdate"], datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
        )

    def test_missing_bib_resource_raises(self):
        empty = (
            '<srw:searchRetrieveResponse '
            'xmlns:srw="http://www.loc.gov/zing/srw/">'
            "<srw:numberOfRecords>0</srw:numberOfRecords>"
            "</srw:searchRetrieveResponse>"
        )
        with self.assertRaises(ValueError):
            parse_sru(empty)


if __name__ == "__main__":
    unittest.main()
