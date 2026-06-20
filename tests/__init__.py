"""Test suite for the MetadataFromASIN package.

Tests use the standard-library ``unittest`` framework only (no third-party
dependencies), in line with the project conventions in AGENTS.md.
"""

import os
import sys

# Ensure the repository root is importable regardless of how the test runner
# is invoked (for example ``python -m unittest discover -s tests``).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
