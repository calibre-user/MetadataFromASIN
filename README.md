# MetadataFromASIN

*日本語の説明は下に続きます。 / English follows the Japanese section.*

---

## 日本語

[Calibre](https://calibre-ebook.com/) 用のメタデータソースプラグインです。
**Amazon の ASIN** から対応する紙書籍の **ISBN** を解決し、その ISBN を使って
[国立国会図書館 (NDL) SRU](https://ndlsearch.ndl.go.jp/) サービスから書誌情報を
補完します。

このツールは 2 通りの使い方ができます。

- **Calibre プラグイン**（メタデータのダウンロードソース）として、
- Calibre をインストールせずに動く **スタンドアロンのコマンドラインスクリプト**
  として。

### 機能

- ASIN から Amazon の商品ページを参照し、ISBN-10 / ISBN-13 を抽出します。
- Amazon からパンくず（タグ）、評価、商品説明を取得します。
- NDL SRU サービスから、タイトル、タイトルソート、シリーズ、著者、著者ソート、
  出版社、言語、出版日を補完します。
- Amazon と NDL の参照は、それぞれ独立して有効・無効を切り替えられます。
- 多数の Amazon ドメイン（`co.jp`, `com`, `co.uk`, `de`, ...）に対応します。

### Calibre プラグインとして使う

1. プラグインの ZIP をビルドします（または
   [Releases](../../releases) ページからダウンロードします）。
   ```sh
   cd MetadataFromASIN
   zip -r ../MetadataFromASIN.zip .
   ```
2. Calibre で **設定 → プラグイン → ファイルからプラグインを読み込む** を開き、
   `MetadataFromASIN.zip` を選択します。
   （開発中は代わりに
   `calibre-customize -b path/to/MetadataFromASIN` を実行できます。）
3. Calibre を再起動します。プラグインは
   **設定 → メタデータのダウンロード** に `MetadataFromASIN` として表示されます。
4. プラグインのオプションで設定します。
   - **Use Amazon** — ISBN やタグなどのために Amazon ページを取得します。
   - **Use NDL SRU** — ISBN を使って NDL から書誌データを補完します。
   - **Amazon domain** — 参照する Amazon サイトを指定します。

書籍が `amazon` / `mobi-asin` 識別子（Amazon を無効にしている場合は ISBN）を
持っているとき、プラグインは Calibre の通常の
*メタデータを編集 → メタデータをダウンロード* の流れでメタデータを提供します。

### スタンドアロンスクリプトとして使う

Calibre のインストールは不要です。パッケージには、使用する Calibre API の最小限の
代替を提供する互換シム（`MetadataFromASIN/calibre_compat.py`）が同梱されています。

```sh
python run_asin.py <ASIN> [domain]
```

例:

```sh
python run_asin.py 4101001014          # ドメイン未指定時は co.jp
python run_asin.py B0XXXXXXXX com
```

解決されたメタデータは標準出力に表示されます。必要なのは Python 3 標準ライブラリ
だけです。

### テスト

テストは標準ライブラリの `unittest` のみで書かれており、`tests/` 以下にあります。
ネットワークアクセスはなく、合成データを使います。次のコマンドで実行できます。

```sh
python -m unittest discover -s tests -t .
```

push と pull request の際には CI（`.github/workflows/ci.yml`）が自動的にテストを
実行します。

### プロジェクト構成

モジュール構成、アーキテクチャの概要、コントリビューションの規約については
[`AGENTS.md`](AGENTS.md) を参照してください。

### リリース

リリースは、`vX.Y.Z` タグがプッシュされたときに GitHub Actions によって自動的に
作成されます（`.github/workflows/release.yml` を参照）。

- `main` から到達できるタグは **latest** リリースとして公開されます。
- `develop` からのみ到達できるタグは **pre-release** として公開されます。

各リリースには、すぐにインストールできる `MetadataFromASIN.zip` が添付されます。

### ライセンス

[MIT License](LICENSE) の下で公開されています。

---

## English

A [Calibre](https://calibre-ebook.com/) metadata source plugin that resolves an
**Amazon ASIN** to the matching physical-book **ISBN**, then enriches the book's
metadata using the [National Diet Library (NDL) SRU](https://ndlsearch.ndl.go.jp/)
service.

It can be used in two ways:

- as a **Calibre plugin** (a metadata download source), and
- as a **standalone command-line script** that runs without Calibre installed.

### Features

- Looks up an Amazon product page by ASIN and extracts the ISBN-10 / ISBN-13.
- Pulls breadcrumb tags, rating, and the product description from Amazon.
- Enriches title, title sort, series, authors, author sort, publisher,
  language, and publication date from the NDL SRU service.
- Amazon and NDL lookups can each be enabled or disabled independently.
- Supports many Amazon domains (`co.jp`, `com`, `co.uk`, `de`, ...).

### Use as a Calibre plugin

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

### Use as a standalone script

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

### Tests

Tests are written with the standard-library `unittest` framework only and live
under `tests/`. They require no network access and use synthetic data. Run them
with:

```sh
python -m unittest discover -s tests -t .
```

CI (`.github/workflows/ci.yml`) runs the test suite automatically on pushes and
pull requests.

### Project layout

See [`AGENTS.md`](AGENTS.md) for the module layout, architecture overview, and
contribution conventions.

### Releases

Releases are produced automatically by GitHub Actions when a `vX.Y.Z` tag is
pushed (see `.github/workflows/release.yml`):

- tags reachable from `main` are published as the **latest** release,
- tags reachable only from `develop` are published as **pre-releases**.

Each release attaches a ready-to-install `MetadataFromASIN.zip`.

### License

Released under the [MIT License](LICENSE).
