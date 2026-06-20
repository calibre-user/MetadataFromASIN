"""Tests for the standalone calibre_compat shims.

These shims are only active when Calibre is not importable. The tests are
skipped when running inside a real Calibre environment.
"""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN import calibre_compat  # noqa: E402


@unittest.skipIf(
    calibre_compat.CALIBRE_AVAILABLE,
    "Standalone shims are only exercised when Calibre is unavailable.",
)
class CheckIsbnShimTests(unittest.TestCase):
    def test_valid_isbn10(self):
        self.assertEqual(calibre_compat.check_isbn("4101001014"), "4101001014")

    def test_valid_isbn10_with_x(self):
        self.assertEqual(calibre_compat.check_isbn("043942089X"), "043942089X")

    def test_valid_isbn13(self):
        self.assertEqual(calibre_compat.check_isbn("9784101001012"), "9784101001012")

    def test_strips_hyphens_and_spaces(self):
        self.assertEqual(calibre_compat.check_isbn("4-10-100101 4"), "4101001014")

    def test_invalid_returns_none(self):
        self.assertIsNone(calibre_compat.check_isbn("1234567890"))


@unittest.skipIf(
    calibre_compat.CALIBRE_AVAILABLE,
    "Standalone shims are only exercised when Calibre is unavailable.",
)
class SanitizeCommentsHtmlTests(unittest.TestCase):
    def test_drops_disallowed_tags(self):
        out = calibre_compat.sanitize_comments_html("<script>alert(1)</script><p>ok</p>")
        self.assertNotIn("script", out)
        self.assertIn("<p>ok</p>", out)

    def test_keeps_safe_href(self):
        out = calibre_compat.sanitize_comments_html('<a href="https://example.com">x</a>')
        self.assertIn('href="https://example.com"', out)

    def test_drops_javascript_scheme_href(self):
        out = calibre_compat.sanitize_comments_html('<a href="javascript:alert(1)">x</a>')
        self.assertIn("<a>", out)
        self.assertNotIn("javascript", out)

    def test_trims_href_before_validating(self):
        out = calibre_compat.sanitize_comments_html('<a href="  https://example.com  ">x</a>')
        self.assertIn('href="https://example.com"', out)

    def test_allows_mailto_scheme(self):
        out = calibre_compat.sanitize_comments_html('<a href="mailto:a@b.com">x</a>')
        self.assertIn('href="mailto:a@b.com"', out)


@unittest.skipIf(
    calibre_compat.CALIBRE_AVAILABLE,
    "Standalone shims are only exercised when Calibre is unavailable.",
)
class ParseOnlyDateShimTests(unittest.TestCase):
    def test_iso_date(self):
        self.assertEqual(
            calibre_compat.parse_only_date("2020-02-03"), datetime.date(2020, 2, 3)
        )

    def test_japanese_year_month(self):
        # "2020\u5e742\u6708" == "2020 year 2 month"; day defaults to 1.
        self.assertEqual(
            calibre_compat.parse_only_date("2020\u5e742\u6708"),
            datetime.date(2020, 2, 1),
        )

    def test_year_only(self):
        self.assertEqual(
            calibre_compat.parse_only_date("2015"), datetime.date(2015, 1, 1)
        )


if __name__ == "__main__":
    unittest.main()
