from __future__ import annotations
"""Calibre plugin: MetadataFromASIN.

Resolves an Amazon ASIN to a physical-book ISBN and enriches metadata using
the National Diet Library (NDL) SRU service. Amazon and NDL lookups can each
be toggled independently through the plugin options.
"""

from typing import Dict, Optional

from .calibre_compat import Metadata, Option, Source
from .config import AMAZON_DOMAINS
from .fetcher import fetch_page
from .metadata import (
    DEFAULT_SRU_FLAGS,
    apply_sru_to_metadata,
    get_metadata_from_asin,
)
from .ndl_sru_parser import parse_sru
from .urls import ndl_sru_url


class MetadataFromASIN(Source):
    name        = 'MetadataFromASIN'
    description = 'ASIN to ISBN & NDL Get Metadata'
    author      = 'Calibre User'
    version     = (1, 0, 0)
    minimum_calibre_version = (5, 0, 0)

    # ------------------------------------------------------------------
    # Fields this plugin may set
    # ------------------------------------------------------------------
    touched_fields = frozenset([
        # identifiers
        'identifier:isbn10',
        'identifier:isbn13',
        'identifier:isbn',

        # core bibliographic fields
        'title',
        'title_sort',
        'authors',
        'author_sort',
        'series',
        'series_index',

        # additional information
        'tags',
        'rating',
        'comments',
        'pubdate',
        'publisher',
        'language',
    ])

    capabilities = frozenset(['identify'])

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------
    options = (
        # 1) Whether to query Amazon
        Option('use_amazon', 'bool', True,
               'Use Amazon', 'Fetch the Amazon page to obtain the ISBN, tags, etc.'),

        # 2) Whether to query NDL (SRU)
        Option('use_ndl', 'bool', True,
               'Use NDL SRU', 'Enrich bibliographic data from the NDL SRU service by ISBN.'),

        # 3) Amazon domain
        Option(
            'domain', 'choices', 'co.jp',
            'Amazon domain', 'Amazon site used for lookups',
            tuple(AMAZON_DOMAINS)
        ),
    )

    # ------------------------------------------------------------------
    # identify()
    # ------------------------------------------------------------------
    def identify(self, log, result_queue, abort,
                 title=None, authors=None, identifiers={}, timeout=30):

        use_amazon = self.prefs.get('use_amazon', True)
        use_ndl    = self.prefs.get('use_ndl',    True)

        # Extract any existing ISBN up front (used when Amazon is disabled).
        isbn: Optional[str] = None
        for key in ('isbn', 'isbn13', 'isbn10'):
            if key in identifiers and identifiers[key]:
                isbn = identifiers[key]
                break

        # --------------------------------------------------------------
        # Amazon enabled: resolve the ISBN and fetch tags/rating/etc.
        # --------------------------------------------------------------
        if use_amazon:
            domain = self.prefs.get('domain', 'co.jp')
            log.info(f"Amazon domain: {domain}")

            key_std = 'amazon_' + domain.replace('.', '_')
            key_alt = 'amazon_jp' if domain == 'co.jp' else None
            allowed = ['mobi-asin', key_std] + ([key_alt] if key_alt else [])

            asin: Optional[str] = None
            for k, v in identifiers.items():
                if k.lower() in allowed and v:
                    asin = str(v).strip()
                    log.info(f"Using ASIN: {asin} (key={k})")
                    break
            if abort.is_set() or not asin:
                return

            sru_flags: Dict[str, bool] = dict(DEFAULT_SRU_FLAGS) if use_ndl else {}

            mi = get_metadata_from_asin(
                asin, domain, log, timeout, fetch_page,
                include_tags     = True,
                include_rating   = True,
                include_comments = True,
                sru_flags        = sru_flags,
            )

            if mi:
                result_queue.put(mi)
            return  # Done once Amazon has been used.

        # --------------------------------------------------------------
        # Amazon disabled: NDL lookup from the existing ISBN only.
        # --------------------------------------------------------------
        if not use_ndl:
            log.info("Both Amazon and NDL are disabled. Nothing to do.")
            return

        if not isbn:
            log.info("No ISBN in the input, so an NDL search cannot be performed.")
            return

        sru_url = ndl_sru_url(isbn)
        log.info(f"SRU URL: {sru_url}")
        xml = fetch_page(sru_url, log, timeout)
        if not xml:
            log.error("SRU fetch failed")
            return

        try:
            sru = parse_sru(xml)
        except Exception as e:
            log.error(f"SRU parse error: {e}")
            return

        mi = Metadata("", [])
        mi.isbn = isbn
        mi.identifiers['isbn'] = isbn
        mi.identifiers['isbn13'] = isbn if len(isbn) == 13 else ''
        mi.identifiers['isbn10'] = isbn if len(isbn) == 10 else ''

        pubdate = apply_sru_to_metadata(mi, sru, DEFAULT_SRU_FLAGS)
        if pubdate:
            mi.pubdate = pubdate

        result_queue.put(mi)
