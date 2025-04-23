# streamlit-starter

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.44+-red.svg)](https://streamlit.io)
[![Shiny](https://img.shields.io/badge/Shiny-1.4+-green.svg)](https://shiny.posit.co/)
[![uv](https://img.shields.io/badge/uv-Package%20Manager-blueviolet)](https://github.com/astral-sh/uv)

> Streamlit / Shiny サンプル付きデータアプリ開発テンプレート

## 🌟 概要

このプロジェクトは、Streamlit / Shiny を使ったデータアプリケーション開発を始めるための基盤となるコードです。複数のサンプルアプリと開発環境が含まれており、すぐに開発を始められます。

### 使用している主要ツール

- **Streamlit**: Pythonでデータアプリを素早く構築できるフレームワーク。データサイエンティストやエンジニアが数行のコードでインタラクティブなアプリを作成できます。
- **Shiny for Python**: R言語から移植されたインタラクティブなWebアプリフレームワーク。より複雑なUI制御が可能です。
- **OpenAI API**: AIを活用した自然言語処理機能を簡単に組み込めます。
- **uv**: Pythonパッケージ管理のための高速な新世代ツール。`pip`と互換性がありながら、より高速で信頼性の高い依存関係管理を実現します。

以下のようなアプリケーションのサンプルが含まれています：

- **CSV データダッシュボード**: データファイルの可視化・分析ツール。データの読み込み、フィルタリング、グラフ表示などの基本的なBI機能を実装。
- **Markdown サマライザー**: OpenAI APIを使ってMarkdownドキュメントを要約し、キーワードを抽出するAI活用アプリ。
- **Shiny デモアプリ**: インタラクティブなデータ可視化と操作が可能なShinyフレームワークのデモ。

## 🚀 始め方

### インストール

プロジェクトのセットアップは`Makefile`を使って簡単に行うことができます：

1. リポジトリをクローンする

   ```sh
   git clone <リポジトリURL>
   cd streamlit-starter
   ```

2. uvをインストールし、依存関係をセットアップする

   ```sh
   make setup  # uvがなければインストール
   make install  # 依存関係をインストール
   make venv  # 仮想環境をアクティブにしてシェルを開く（オプション）
   ```

3. 環境変数を設定する（必要な場合）

   ```sh
   cp .env.example .env
   # .envファイルを編集（Markdownサマライザーを使用する場合はOPENAI_API_KEYが必要）
   ```

> **注意**: `uv`を手動でインストールする場合は `curl -LsSf https://astral.sh/uv/install.sh | sh` を実行し、
依存関係を手動でインストールする場合は `uv sync` を実行します。

## 🛠️ Makefileを使った操作

このプロジェクトには、開発作業を効率化するための`Makefile`が用意されています。これにより、複雑なコマンドを簡単に実行できます。

```sh
# 利用可能なコマンド一覧を表示（自己ドキュメント機能）
make help
```

### セットアップと依存関係

```sh
# uvがなければインストール
make setup

# 依存関係をインストール
make install

# 仮想環境をアクティブにしてシェルを開く
make venv

# pre-commitフックをインストール
make pre-commit
```

### アプリケーションの実行

```sh
# CSVダッシュボードを実行（http://localhost:8501
make run-csv

# Markdownサマライザーを実行（http://localhost:8502）
# OpenAI APIキーが必要です
make run-markdown

# Shinyデモアプリを実行（http://localhost:8503）
make run-shiny

# 任意のアプリを実行（パスとポートを指定）
make run APP=src/my_app/main.py PORT=8505
```

> **備考**: 上記のmakeコマンドは内部的に次のようなコマンドを実行しています:
>
> - CSVダッシュボード: `uv run streamlit run src/csv_dashboard/main.py`
> - Markdownサマライザー: `uv run streamlit run src/markdown_summarizer/main.py`
> - Shinyデモ: `uv run shiny run src/shiny_demo/main.py`

### Docker関連のコマンド

```sh
# Dockerイメージをビルド
make docker-build

# CSVダッシュボードをDockerで実行
make docker-run-csv

# Markdownサマライザーをドッカーで実行（APIキーが必要）
make docker-run-markdown

# ShinyデモアプリをDockerで実行
make docker-run-shiny

# 任意のアプリをDockerで実行
make docker-run APP=my_app
```

> **備考**: Dockerコマンドは内部的に
`docker run -p 8501:8501 [-e OPENAI_API_KEY=your_api_key] streamlit-starter [アプリ名]`
のようなコマンドを実行しています。
Dockerコンテナ内では`launch.sh`スクリプトを使用してアプリケーションが起動され、コンテナ外部からアクセスできるようにポートが公開されます。

### メンテナンス

```sh
# キャッシュファイルと一時ファイルを削除
make clean
```

## 📁 ディレクトリ構成

```txt
streamlit-starter/
├── .devcontainer/   # VS Code開発コンテナ設定
│   ├── devcontainer.json  # 開発コンテナの設定ファイル
│   └── Dockerfile         # 開発環境用Dockerfile
├── .github/         # GitHub Actions設定
├── infra/           # インフラ関連ファイル
├── scripts/         # ユーティリティスクリプト
│   └── launch.sh    # アプリケーション起動スクリプト
├── src/             # ソースコード
│   ├── csv_dashboard/       # CSVダッシュボードアプリ
│   ├── libs/                # 共通ライブラリ
│   │   └── settings.py      # 共通設定
│   ├── markdown_summarizer/ # Markdownサマライザーアプリ
│   └── shiny_demo/          # Shinyデモアプリ
├── .env.example     # 環境変数サンプル（OPENAI_API_KEY等）
├── .gitignore       # Gitの除外ファイル設定
├── .python-version  # Pythonバージョン指定（3.13）
├── Dockerfile       # 本番環境用Dockerコンテナ設定
├── LICENSE          # ライセンス情報
├── Makefile         # 開発用コマンド集
├── README.md        # このファイル
├── pyproject.toml   # プロジェクト設定と依存関係
└── uv.lock          # uvによる依存関係ロックファイル
```

## 🛠️ 開発のヒント

### 新しいStreamlitアプリの作成

1. `src/`ディレクトリに新しいフォルダを作成（例: `my_app`）
2. フォルダ内に`__init__.py`と`main.py`を作成
3. Streamlitのコードを`main.py`に記述
4. 実行するには: `make run APP=src/my_app/main.py PORT=8504`

### 新しいアプリをlaunch.shに追加する

新しいアプリを作成した場合、`scripts/launch.sh`に起動コマンドを追加することで、簡単に実行できるようになります：

```bash
# scripts/launch.shに追加
my_app )
  exec uv run streamlit run src/my_app/main.py \
       --server.address=0.0.0.0 ;;
```

### Makefileに新しいアプリを追加する

新しいアプリを作成した場合、Makefileにも追加すると便利です：

```makefile
# 変数の定義を追加
MY_APP := src/my_app/main.py
MY_PORT ?= 8504

# 実行コマンドを追加
.PHONY: run-my-app
run-my-app: ## My Appの説明（help表示用）
    $(STREAMLIT_CMD) $(MY_APP) --server.port $(MY_PORT)
```

### カスタマイズとベストプラクティス

- 共通の設定は`src/libs/settings.py`に追加
- 環境変数は`.env`ファイルを使って管理
- 共通して利用できそうな機能は適切な関数に分割して `src/libs` に追加

### コードリンターとフォーマッターの設定

#### ruffのルール緩和について

このプロジェクトでは、コードの品質を維持するために[ruff](https://github.com/astral-sh/ruff)というPythonリンターを使用しています。デフォルトでは厳格なルールが適用されていますが、必要に応じて`pyproject.toml`ファイルの`ignore`セクションにルールを追加することで緩和できます。

```toml
[tool.ruff.lint]
extend-select = ["ALL"]
# 現在厳しいルールを設定しています。必要に応じてignoreに追加することで緩和してください。
ignore = [
    "D",      # ドキュメンテーション関連のルール
    "E501",   # 行の長さのルール
    "COM",    # コンマ配置のルール
    "T201",   # print文の使用に関するルール
    # その他必要に応じてここにルールを追加
]
```

### uvを使ったパッケージの追加方法

このプロジェクトでは、パッケージ管理に`uv`を使用しています。新しいパッケージを追加するには以下の方法があります：

```sh
# 基本的な使い方
uv add パッケージ名

# バージョンを指定して追加
uv add パッケージ名==バージョン

# 開発用パッケージの追加
uv add --dev パッケージ名
```

パッケージを追加すると、自動的に以下のファイルが更新されます：

- `pyproject.toml`: パッケージの依存関係情報
- `uv.lock`: 正確なバージョン情報を含むロックファイル

## 🔧 開発環境

このプロジェクトはVS Codeの開発コンテナに対応しています。開発コンテナを使用すると、チーム全体で一貫した開発環境を簡単に構築できます。

### 開発コンテナの使用方法

1. VS Codeと[Remote - Containers拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)をインストールします。

2. プロジェクトをVS Codeで開き、左下の緑色のアイコンをクリックして、「Reopen in Container」を選択します。

3. VS Codeは`.devcontainer`の設定を使用して、開発環境を自動的に構築します：
   - Python 3.13
   - uv依存関係管理ツール
   - 必要なライブラリ（Streamlit、Shiny、OpenAIなど）
   - コード品質ツール（linter、formatter）

4. コンテナ内では、ターミナルからすぐにアプリケーションを実行できます：

   ```sh
   make run-csv
   ```

### pre-commitフック

このプロジェクトでは`.pre-commit-config.yaml`を使用して、コードの品質を維持するための自動チェックを行います。開発環境では以下のようにインストールして使用できます：

```sh
make pre-commit
```

これにより、コミット前に自動的にコードの品質チェックが行われます。
