"""Tests for text_utils: separator and comma normalization."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.text_utils import clean_commas, normalize_sep  # noqa: E402


class NormalizeSepTests(unittest.TestCase):
    def test_ascii_semicolon(self):
        self.assertEqual(normalize_sep("A; B"), "A : B")

    def test_fullwidth_semicolon(self):
        # "\uFF1B" is the full-width semicolon.
        self.assertEqual(normalize_sep("A\uFF1BB"), "A : B")

    def test_trims_surrounding_whitespace(self):
        self.assertEqual(normalize_sep("  Title  "), "Title")

    def test_no_separator_is_unchanged(self):
        self.assertEqual(normalize_sep("Plain Title"), "Plain Title")


class CleanCommasTests(unittest.TestCase):
    def test_comma_becomes_space(self):
        self.assertEqual(clean_commas("Last, First"), "Last First")

    def test_collapses_repeated_whitespace(self):
        self.assertEqual(clean_commas("a    b   c"), "a b c")

    def test_trims_surrounding_whitespace(self):
        self.assertEqual(clean_commas("  hello  "), "hello")


if __name__ == "__main__":
    unittest.main()
