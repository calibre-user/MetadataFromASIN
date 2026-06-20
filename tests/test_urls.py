"""Tests for urls: Amazon product and NDL SRU URL builders."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.urls import amazon_product_url, ndl_sru_url  # noqa: E402


class AmazonProductUrlTests(unittest.TestCase):
    def test_co_jp_domain(self):
        self.assertEqual(
            amazon_product_url("4101001014", "co.jp"),
            "https://www.amazon.co.jp/dp/4101001014",
        )

    def test_com_domain(self):
        self.assertEqual(
            amazon_product_url("B0XXXXXXXX", "com"),
            "https://www.amazon.com/dp/B0XXXXXXXX",
        )


class NdlSruUrlTests(unittest.TestCase):
    def test_embeds_isbn(self):
        url = ndl_sru_url("9784101001012")
        self.assertIn("query=isbn=9784101001012", url)

    def test_uses_ndl_sru_endpoint(self):
        url = ndl_sru_url("9784101001012")
        self.assertTrue(url.startswith("https://ndlsearch.ndl.go.jp/api/sru?"))
        self.assertIn("operation=searchRetrieve", url)


if __name__ == "__main__":
    unittest.main()
