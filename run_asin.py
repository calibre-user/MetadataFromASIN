#!/usr/bin/env python3
"""Standalone runner: resolve a physical-book ISBN (and metadata) from an ASIN.

Runs the MetadataFromASIN plugin outside of Calibre, using the compatibility
shims in ``MetadataFromASIN.calibre_compat``.

Usage:
    python run_asin.py ASIN [domain]
"""

import importlib
import os
import sys
from queue import Queue


class Abort:
    def is_set(self):
        return False


class DummyLog:
    def info(self, msg):  print(msg)
    def debug(self, msg): print(msg)
    def error(self, msg): print(msg)


def main():
    if len(sys.argv) < 2:
        print("Usage: run_asin.py ASIN [domain]")
        sys.exit(1)
    asin = sys.argv[1]
    domain = sys.argv[2] if len(sys.argv) > 2 else 'co.jp'

    # 1) Add the plugin folder to sys.path.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(script_dir, 'MetadataFromASIN')
    if plugin_dir not in sys.path:
        sys.path.insert(0, plugin_dir)

    # 2) Import the package and obtain the plugin class.
    try:
        plugin_module = importlib.import_module('MetadataFromASIN')
        plugin_cls = getattr(plugin_module, 'MetadataFromASIN')
    except Exception as e:
        print(f"Failed to import the plugin: {e}")
        sys.exit(1)

    # 3) Instantiate the plugin (passing plugin_path when supported).
    try:
        plugin = plugin_cls(plugin_dir)
    except TypeError:
        # Older Calibre versions may not require plugin_path.
        plugin = plugin_cls()
    # Apply the domain setting.
    plugin.prefs.set('domain', domain)

    # 4) Run identify().
    log = DummyLog()
    q = Queue()
    abort = Abort()
    plugin.identify(log, q, abort, identifiers={'mobi-asin': asin})

    # 5) Print the results.
    while not q.empty():
        mi = q.get()
        print(mi)


if __name__ == '__main__':
    main()
