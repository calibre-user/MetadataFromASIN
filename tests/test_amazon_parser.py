"""Tests for amazon_parser.parse_amazon_page using synthetic HTML."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.amazon_parser import parse_amazon_page  # noqa: E402


class _Log:
    def info(self, msg):
        pass

    def debug(self, msg):
        pass

    def error(self, msg):
        pass


# Amazon breadcrumbs are separated by "\u203a" (single right angle quote).
_SAMPLE_HTML = (
    "<html><body>"
    '<a href="/dp/4101001014">product</a>'
    '<div id="wayfinding-breadcrumbs_feature_div">'
    "<ul><li><span>Books</span></li>"
    "<li><span>\u203a</span></li>"
    "<li><span>Fiction</span></li></ul></div>"
    '<span id="acrPopover" title="4.5 out of 5 stars"></span>'
    '<div id="bookDescription_feature_div"><p>Hello description</p></div>'
    "</body></html>"
)


class ParseAmazonPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = parse_amazon_page(_SAMPLE_HTML, _Log())

    def test_isbn10_extracted(self):
        self.assertEqual(self.result["isbn10"], "4101001014")

    def test_isbn13_derived(self):
        self.assertEqual(self.result["isbn13"], "9784101001012")

    def test_tags_split_on_breadcrumb_separator(self):
        self.assertEqual(self.result["tags"], ["Books", "Fiction"])

    def test_rating_parsed(self):
        self.assertEqual(self.result["rating"], 4.5)

    def test_comments_contain_description(self):
        self.assertIn("Hello description", self.result["comments"])

    def test_missing_slug_raises(self):
        with self.assertRaises(ValueError):
            parse_amazon_page("<html><body>no product link</body></html>", _Log())


if __name__ == "__main__":
    unittest.main()
