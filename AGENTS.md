# Contributor & Agent Guidelines / コントリビューター・エージェント向けガイドライン

These conventions apply to all contributors (human or automated) working in
this repository.

このリポジトリで作業するすべてのコントリビューター（人間・自動化エージェントを
問わず）に、以下の規約が適用されます。

*日本語の説明は下に続きます。 / English follows the Japanese section.*

---

## 日本語

### 言語ポリシー

- **コード**（ソースコード、コメント、docstring、識別子、ログメッセージ）は、
  **英語かつ ASCII 文字のみ** で記述してください。
- **ドキュメント**（`README.md`、`README_ja.md`、`AGENTS.md` などの Markdown
  ファイル）は日本語で記述してよく、**日英併記が理想** です。本プロジェクトは主に日本語の
  書籍メタデータを扱うため、日本語話者向けの説明があると役立ちます。
- 本プロジェクトは日本語の書籍メタデータを解析するので、一部の正規表現は日本語
  テキストにマッチする必要があります。そうした非 ASCII 文字は Python の Unicode
  エスケープ（例: 「年」を表す `\u5e74`）として表現し、そのパターンが何にマッチ
  するかを説明する短い英語のコメントを添えてください。
- コードの中（コメントや文字列リテラルなど）には日本語テキストを残さないで
  ください。日本語はドキュメントと、上記の Unicode エスケープに限定します。

### プロジェクト構成

```
MetadataFromASIN/            # Calibre プラグインパッケージ
├── __init__.py             # プラグインのエントリポイント (Source サブクラス) + オーケストレーション
├── calibre_compat.py       # Calibre の有無にかかわらず動かすためのシム
├── config.py               # 共有の定数とセレクタ
├── fetcher.py              # HTTP 取得ヘルパー
├── urls.py                 # URL ビルダー (Amazon 商品 / NDL SRU)
├── amazon_parser.py        # Amazon 商品ページの HTML パーサー
├── ndl_sru_parser.py       # NDL SRU の XML パーサー
├── metadata.py             # Amazon + NDL を Metadata オブジェクトに統合
├── isbn_utils.py           # ISBN の正規化 / 変換
├── date_utils.py           # 出版日の解析
└── text_utils.py           # 文字列正規化ヘルパー
run_asin.py                 # スタンドアロン CLI ランナー (Calibre 不要)
```

### アーキテクチャ

このコードは、シンプルで読みやすく拡張しやすいコードベースを目指して、小さな
レイヤード設計を採用しています。

- **互換レイヤー** (`calibre_compat.py`) は Calibre のインポートをすべて隔離し、
  同じパッケージが Calibre 内でもスタンドアロンでも動くようにします。
- **I/O レイヤー** (`fetcher.py`, `urls.py`) はネットワークアクセスと URL の
  構築を担います。
- **パーサーレイヤー** (`amazon_parser.py`, `ndl_sru_parser.py`) は生の
  HTML/XML をプレーンな辞書に変換し、Calibre への依存を持ちません。
- **オーケストレーション** (`metadata.py`, `__init__.py`) はパーサーを組み合わせ、
  結果を Calibre の `Metadata` オブジェクトにマッピングします。
- **ユーティリティ** (`isbn_utils.py`, `date_utils.py`, `text_utils.py`) は
  小さく再利用可能で副作用のないヘルパーを保持します。

共有ロジック（URL の構築、出版日の解析、SRU からメタデータへのマッピング）は
一箇所にまとめられ、プラグインとスタンドアロンランナーの両方で再利用されます。

### 開発

- Python 3 と標準ライブラリのみを対象とします（サードパーティのランタイム依存は
  なし）。
- 簡易チェック: `python -m py_compile MetadataFromASIN/*.py run_asin.py`。
- 手動実行: `python run_asin.py <ASIN> [domain]`。

### テスト

- テストは標準ライブラリの `unittest` だけで記述します（pytest などのサード
  パーティ依存は追加しません）。テストは `tests/` 以下にあります。
- 全テストを実行: `python -m unittest discover -s tests -t .`。
- テストはネットワークにアクセスしません。HTTP 取得はスタブし、`tests/fixtures/`
  の合成データを使います。
- テストコードも言語ポリシーに従い、コメント・文字列は英語/ASCII のみとします。
  日本語の入力が必要な箇所は Unicode エスケープで表現してください。
- CI（`.github/workflows/ci.yml`）が push（`main` / `develop`）と pull request
  の際に、バイトコンパイルチェックと `unittest` スイートを複数の Python
  バージョンで実行します。

### ブランチとリリース

- `main` と `develop` は保護されています。直接プッシュせず、プルリクエストを
  作成してください。
- `main` は `latest` リリースを生成し、`develop` は pre-release を生成します。
- リリースは `vX.Y.Z` タグがプッシュされたときに自動的に公開されます
  （`.github/workflows/release.yml` を参照）。バージョンは `v0.0.1` から始まります。

### ワークフロー

`develop` は保護されており直接 push できないため、すべての変更は以下の手順で
適用してください。人間・自動化エージェントを問わず、この手順を必ず守ります。

1. **最新状態の確認から始める**: 作業を始める前に必ず `git fetch` と `git pull`
   を実行し、リモートの最新変更を取り込んでください。
   ```sh
   git fetch --all --prune
   git checkout develop
   git pull --ff-only
   ```
2. **作業ブランチを作成する**: `develop` から新しいブランチを切ります。
   ```sh
   git checkout -b <type>/<short-description>
   ```
   例: `feature/sru-pagination`, `fix/isbn-normalization`, `docs/readme-split`
3. **変更を加える**: コード・ドキュメントを編集し、テストと
   `python -m py_compile MetadataFromASIN/*.py run_asin.py` で確認します。
4. **コミットする**: 意味のある単位でコミットします。
   ```sh
   git add <files>
   git commit -m "<short English message>"
   ```
5. **プッシュする**: 作業ブランチをリモートに push します。
   ```sh
   git push -u origin <branch>
   ```
6. **プルリクエストを作成する**: `<branch>` → `develop` の PR を作成し、CI と
   レビューを経てからマージします。`develop` への直接 push は禁止です。

要点:

- **`develop` への直接 push は不可**。常にブランチを作成し、PR 経由で変更を適用
  する。
- **作業開始時は必ず `git fetch` / `git pull` で最新化する**。
- **コミットとプッシュも必ず行う**。ローカルに未 push の変更を残さない。

---

## English

### Language policy

- **Code** (source code, comments, docstrings, identifiers, log messages) must
  be written in **English using ASCII-only characters**. 
- **Documentation** (Markdown files such as `README.md`, `README_ja.md`, and
  `AGENTS.md`) may be written in Japanese and is **ideally bilingual (Japanese +
  English)**. The
  project mainly deals with Japanese book metadata, so explanations aimed at
  Japanese speakers are helpful.
- The project parses Japanese book metadata, so some regular expressions must
  match Japanese text. Express any such non-ASCII characters as Python Unicode
  escapes (for example `\u5e74` for the "year" kanji) and add a short English
  comment explaining what the pattern matches.
- Do not leave Japanese text inside code (for example in comments or string
  literals). Japanese is limited to documentation and to the Unicode escapes
  described above.

### Project layout

```
MetadataFromASIN/            # The Calibre plugin package
├── __init__.py             # Plugin entry point (Source subclass) + orchestration
├── calibre_compat.py       # Shims so the package runs with or without Calibre
├── config.py               # Shared constants and selectors
├── fetcher.py              # HTTP fetch helper
├── urls.py                 # URL builders (Amazon product / NDL SRU)
├── amazon_parser.py        # Amazon product-page HTML parser
├── ndl_sru_parser.py       # NDL SRU XML parser
├── metadata.py             # Orchestrates Amazon + NDL into a Metadata object
├── isbn_utils.py           # ISBN normalization / conversion
├── date_utils.py           # Publication-date parsing
└── text_utils.py           # String normalization helpers
run_asin.py                 # Standalone CLI runner (no Calibre required)
```

### Architecture

The code follows a small layered design chosen for a simple, readable, and
extensible codebase:

- **Compatibility layer** (`calibre_compat.py`) isolates every Calibre import so
  the same package runs inside Calibre or standalone.
- **I/O layer** (`fetcher.py`, `urls.py`) handles network access and URL
  construction.
- **Parser layer** (`amazon_parser.py`, `ndl_sru_parser.py`) turns raw
  HTML/XML into plain dictionaries and has no Calibre dependency.
- **Orchestration** (`metadata.py`, `__init__.py`) combines the parsers and maps
  results onto a Calibre `Metadata` object.
- **Utilities** (`isbn_utils.py`, `date_utils.py`, `text_utils.py`) hold small,
  reusable, side-effect-free helpers.

Shared logic (URL building, date parsing, SRU-to-metadata mapping) lives in a
single place and is reused by both the plugin and the standalone runner.

### Development

- Target Python 3 and the standard library only (no third-party runtime deps).
- Quick check: `python -m py_compile MetadataFromASIN/*.py run_asin.py`.
- Manual run: `python run_asin.py <ASIN> [domain]`.

### Tests

- Tests are written with the standard-library `unittest` framework only (no
  third-party dependencies such as pytest). They live under `tests/`.
- Run all tests: `python -m unittest discover -s tests -t .`.
- Tests never touch the network: HTTP fetches are stubbed and synthetic data in
  `tests/fixtures/` is used.
- Test code follows the language policy too: comments and strings are
  English/ASCII only; express any required Japanese input as Unicode escapes.
- CI (`.github/workflows/ci.yml`) runs the byte-compile check and the `unittest`
  suite across several Python versions on pushes (`main` / `develop`) and pull
  requests.

### Branching & releases

- `main` and `develop` are protected; do not push to them directly. Open a pull
  request instead.
- `main` produces the `latest` release; `develop` produces pre-releases.
- Releases are published automatically when a `vX.Y.Z` tag is pushed
  (see `.github/workflows/release.yml`). Versioning starts at `v0.0.1`.

### Workflow

`develop` is protected and cannot be pushed to directly, so every change must
be applied through the following steps. Both human and automated contributors
must follow this procedure.

1. **Start by syncing the latest state**: before any work, always run
   `git fetch` and `git pull` to incorporate the latest remote changes.
   ```sh
   git fetch --all --prune
   git checkout develop
   git pull --ff-only
   ```
2. **Create a working branch**: branch off from `develop`.
   ```sh
   git checkout -b <type>/<short-description>
   ```
   Examples: `feature/sru-pagination`, `fix/isbn-normalization`,
   `docs/readme-split`
3. **Make changes**: edit code or documentation, then verify with tests and
   `python -m py_compile MetadataFromASIN/*.py run_asin.py`.
4. **Commit**: commit in meaningful units.
   ```sh
   git add <files>
   git commit -m "<short English message>"
   ```
5. **Push**: push the working branch to the remote.
   ```sh
   git push -u origin <branch>
   ```
6. **Open a pull request**: open a PR from `<branch>` to `develop`. It must pass
   CI and review before merging. Direct pushes to `develop` are forbidden.

Key points:

- **Never push directly to `develop`**. Always create a branch and apply changes
  through a PR.
- **Always start work with `git fetch` / `git pull`** to stay up to date.
- **Always commit and push**. Do not leave unpushed changes locally.
