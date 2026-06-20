# MetadataFromASIN

[English README](README.md) / [コントリビューション規約](AGENTS.md)

---

[Calibre](https://calibre-ebook.com/) 用のメタデータソースプラグインです。
**Amazon の ASIN** から対応する紙書籍の **ISBN** を解決し、その ISBN を使って
[国立国会図書館 (NDL) SRU](https://ndlsearch.ndl.go.jp/) サービスから書誌情報を
補完します。

このツールは 2 通りの使い方ができます。

- **Calibre プラグイン**（メタデータのダウンロードソース）として、
- Calibre をインストールせずに動く **スタンドアロンのコマンドラインスクリプト**
  として。

## 機能

- ASIN から Amazon の商品ページを参照し、ISBN-10 / ISBN-13 を抽出します。
- Amazon からパンくず（タグ）、評価、商品説明を取得します。
- NDL SRU サービスから、タイトル、タイトルソート、シリーズ、著者、著者ソート、
  出版社、言語、出版日を補完します。
- Amazon と NDL の参照は、それぞれ独立して有効・無効を切り替えられます。
- 多数の Amazon ドメイン（`co.jp`, `com`, `co.uk`, `de`, ...）に対応します。

## Calibre プラグインとして使う

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

## スタンドアロンスクリプトとして使う

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

## テスト

テストは標準ライブラリの `unittest` のみで書かれており、`tests/` 以下にあります。
ネットワークアクセスはなく、合成データを使います。次のコマンドで実行できます。

```sh
python -m unittest discover -s tests -t .
```

push と pull request の際には CI（`.github/workflows/ci.yml`）が自動的にテストを
実行します。

## プロジェクト構成

モジュール構成、アーキテクチャの概要、コントリビューションの規約については
[`AGENTS.md`](AGENTS.md) を参照してください。

## リリース

リリースは、`vX.Y.Z` タグがプッシュされたときに GitHub Actions によって自動的に
作成されます（`.github/workflows/release.yml` を参照）。

- `main` から到達できるタグは **latest** リリースとして公開されます。
- `develop` からのみ到達できるタグは **pre-release** として公開されます。

各リリースには2つのダウンロード用アーカイブが添付されます:

- `MetadataFromASIN.zip` — Calibre プラグイン本体（*設定 → プラグイン →
  ファイルからプラグインを読み込む* でインストール）。
- `MetadataFromASIN-standalone.zip` — `run_asin.py`、`README.md`、`LICENSE`、
  `MetadataFromASIN/` プラグインパッケージを同梱したスタンドアロン版。
  展開して `python run_asin.py <ASIN> [domain]` を実行すれば、Calibre の
  インストールなしでメタデータを取得できます。

## ライセンス

[MIT License](LICENSE) の下で公開されています。
