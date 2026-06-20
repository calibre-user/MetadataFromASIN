"""Tests for isbn_utils: ISBN-10/13 normalization and conversion."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MetadataFromASIN.isbn_utils import (  # noqa: E402
    convert_isbn10_to_isbn13,
    normalize_isbn10,
    normalize_isbn13,
)


class NormalizeIsbn10Tests(unittest.TestCase):
    def test_valid_plain(self):
        self.assertEqual(normalize_isbn10("4101001014"), "4101001014")

    def test_valid_with_hyphens_and_spaces(self):
        self.assertEqual(normalize_isbn10(" 4-10-100101-4 "), "4101001014")

    def test_valid_with_trailing_x_check_digit(self):
        # 043942089X is a well-formed ISBN-10 ending in the X check digit.
        self.assertEqual(normalize_isbn10("043942089X"), "043942089X")

    def test_lowercase_x_is_accepted(self):
        self.assertEqual(normalize_isbn10("043942089x"), "043942089X")

    def test_invalid_check_digit_returns_none(self):
        self.assertIsNone(normalize_isbn10("4101001011"))

    def test_wrong_length_returns_none(self):
        self.assertIsNone(normalize_isbn10("123"))


class NormalizeIsbn13Tests(unittest.TestCase):
    def test_valid_plain(self):
        self.assertEqual(normalize_isbn13("9784101001012"), "9784101001012")

    def test_valid_with_separators(self):
        self.assertEqual(normalize_isbn13("978-4-10-100101-2"), "9784101001012")

    def test_invalid_check_digit_returns_none(self):
        self.assertIsNone(normalize_isbn13("9784101001019"))

    def test_wrong_length_returns_none(self):
        self.assertIsNone(normalize_isbn13("97841010010"))


class ConvertIsbn10ToIsbn13Tests(unittest.TestCase):
    def test_known_conversion(self):
        self.assertEqual(convert_isbn10_to_isbn13("4101001014"), "9784101001012")

    def test_conversion_accepts_separators(self):
        self.assertEqual(convert_isbn10_to_isbn13("4-10-100101-4"), "9784101001012")

    def test_invalid_input_returns_none(self):
        self.assertIsNone(convert_isbn10_to_isbn13("4101001011"))


if __name__ == "__main__":
    unittest.main()
