# MetadataFromASIN

[日本語版 README はこちら](README_ja.md) / [Contributor guidelines](AGENTS.md)

---

A [Calibre](https://calibre-ebook.com/) metadata source plugin that resolves an
**Amazon ASIN** to the matching physical-book **ISBN**, then enriches the book's
metadata using the [National Diet Library (NDL) SRU](https://ndlsearch.ndl.go.jp/)
service.

It can be used in two ways:

- as a **Calibre plugin** (a metadata download source), and
- as a **standalone command-line script** that runs without Calibre installed.

## Features

- Looks up an Amazon product page by ASIN and extracts the ISBN-10 / ISBN-13.
- Pulls breadcrumb tags, rating, and the product description from Amazon.
- Enriches title, title sort, series, authors, author sort, publisher,
  language, and publication date from the NDL SRU service.
- Amazon and NDL lookups can each be enabled or disabled independently.
- Supports many Amazon domains (`co.jp`, `com`, `co.uk`, `de`, ...).

## Use as a Calibre plugin

1. Build the plugin ZIP (or download it from the
   [Releases](../../releases) page):
   ```sh
   cd MetadataFromASIN
   zip -r ../MetadataFromASIN.zip .
   ```
2. In Calibre: **Preferences → Plugins → Load plugin from file**, then select
   `MetadataFromASIN.zip`.
   (During development you can instead run
   `calibre-customize -b path/to/MetadataFromASIN`.)
3. Restart Calibre. The plugin appears under
   **Preferences → Metadata download** as `MetadataFromASIN`.
4. Configure it via the plugin options:
   - **Use Amazon** — fetch the Amazon page for the ISBN, tags, etc.
   - **Use NDL SRU** — enrich bibliographic data from the NDL by ISBN.
   - **Amazon domain** — which Amazon site to query.

The plugin contributes metadata during Calibre's normal
*Edit metadata → Download metadata* flow when the book has an
`amazon`/`mobi-asin` identifier (or an ISBN, when Amazon is disabled).

## Use as a standalone script

No Calibre installation is required — the package ships with compatibility
shims (`MetadataFromASIN/calibre_compat.py`) that provide minimal replacements
for the Calibre APIs it uses.

```sh
python run_asin.py <ASIN> [domain]
```

Examples:

```sh
python run_asin.py 4101001014          # defaults to the co.jp domain
python run_asin.py B0XXXXXXXX com
```

The resolved metadata is printed to stdout. Only the Python 3 standard library
is required.

## Tests

Tests are written with the standard-library `unittest` framework only and live
under `tests/`. They require no network access and use synthetic data. Run them
with:

```sh
python -m unittest discover -s tests -t .
```

CI (`.github/workflows/ci.yml`) runs the test suite automatically on pushes and
pull requests.

## Project layout

See [`AGENTS.md`](AGENTS.md) for the module layout, architecture overview, and
contribution conventions.

## Releases

Releases are produced automatically by GitHub Actions when a `vX.Y.Z` tag is
pushed (see `.github/workflows/release.yml`):

- tags reachable from `main` are published as the **latest** release,
- tags reachable only from `develop` are published as **pre-releases**.

Each release attaches two downloadable archives:

- `MetadataFromASIN.zip` — the Calibre plugin (install via
  *Preferences → Plugins → Load plugin from file*).
- `MetadataFromASIN-standalone.zip` — a standalone package containing
  `run_asin.py`, `README.md`, `LICENSE`, and the `MetadataFromASIN/` plugin
  package. Unzip it and run `python run_asin.py <ASIN> [domain]` without
  installing Calibre.

## License

Released under the [MIT License](LICENSE).
