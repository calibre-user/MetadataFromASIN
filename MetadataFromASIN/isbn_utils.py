import re
from typing import Optional

from .calibre_compat import check_isbn
from .config import ISBN10_REGEX, ISBN13_REGEX

def normalize_isbn10(isbn10: str) -> Optional[str]:
    """Normalize an ISBN-10-like string and validate it via check_isbn.

    Returns None when the value is not a valid ISBN-10.
    """
    s = isbn10.upper().replace('-', '').strip()
    return check_isbn(s) if ISBN10_REGEX.match(s) else None

def normalize_isbn13(isbn13: str) -> Optional[str]:
    """Normalize an ISBN-13-like string and validate it via check_isbn.

    Returns None when the value is not a valid ISBN-13.
    """
    digits = re.sub(r'\D', '', isbn13)
    return check_isbn(digits) if ISBN13_REGEX.match(digits) else None

def convert_isbn10_to_isbn13(isbn10: str) -> Optional[str]:
    """Convert an ISBN-10 to a normalized ISBN-13. Returns None on failure."""
    valid10 = normalize_isbn10(isbn10)
    if not valid10:
        return None
    body = '978' + valid10[:-1]
    total = sum((int(ch) if idx % 2 == 0 else int(ch) * 3)
                for idx, ch in enumerate(body))
    check = (10 - total % 10) % 10
    return normalize_isbn13(body + str(check))
