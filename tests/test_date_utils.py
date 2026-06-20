"""Tests for date_utils.parse_pubdate."""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.calibre_compat import utc_tz  # noqa: E402
from MetadataFromASIN.date_utils import parse_pubdate  # noqa: E402


class ParsePubdateTests(unittest.TestCase):
    def test_japanese_full_date(self):
        # "2020\u5e741\u670815\u65e5" == "2020 year 1 month 15 day".
        result = parse_pubdate("2020\u5e741\u670815\u65e5")
        self.assertEqual(result, datetime.datetime(2020, 1, 15, tzinfo=utc_tz))

    def test_iso_dashed_date(self):
        result = parse_pubdate("2019-03-07")
        self.assertEqual(result, datetime.datetime(2019, 3, 7, tzinfo=utc_tz))

    def test_iso_slashed_date(self):
        result = parse_pubdate("2018/12/01")
        self.assertEqual(result, datetime.datetime(2018, 12, 1, tzinfo=utc_tz))

    def test_year_only_fallback(self):
        result = parse_pubdate("Published 2017")
        self.assertEqual(result, datetime.datetime(2017, 1, 1, tzinfo=utc_tz))

    def test_unparseable_returns_none(self):
        self.assertIsNone(parse_pubdate("no date here"))

    def test_result_is_timezone_aware_utc(self):
        result = parse_pubdate("2021-05-09")
        self.assertIsNotNone(result.tzinfo)
        self.assertEqual(result.utcoffset(), datetime.timedelta(0))


if __name__ == "__main__":
    unittest.main()
