#################################################################
# Makefile — streamlit‑starter
# -------------------------------------------------------------
#   * 変数にまとめて環境差分を吸収
#   * .PHONY でファイル生成の無いターゲット宣言
#   * `make help` で自己ドキュメント化
#   * ポータビリティの高い POSIX Bash / fail‑fast
#################################################################

# --------------------------------------------------------------
# 基本設定 – 必要に応じて上書き (`make XXX VAR=value`)
# --------------------------------------------------------------
SHELL           := bash
.SHELLFLAGS     := -euo pipefail -c

STREAMLIT_CMD   := uv run streamlit run
SHINY_CMD       := uv run shiny run

CSV_APP        := src/csv_dashboard/main.py
MD_APP         := src/markdown_summarizer/main.py
SHINY_APP      := src/shiny_demo/main.py

DOCKER_IMAGE   ?= streamlit-starter

# --------------------------------------------------------------
# 自動ドキュメント (`make help`)
# --------------------------------------------------------------
.PHONY: help
help:  ## コマンド一覧を表示
	@grep -E "^[0-9A-Za-z_-]+:.*?##" $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS=":.*?##"}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}' | sort

# --------------------------------------------------------------
# セットアップ & 依存関係
# --------------------------------------------------------------
.PHONY: setup
setup: ## uv が無ければインストール (一度だけ実行)
	@command -v uv >/dev/null 2>&1 || \
	  (echo "uv が見つかりません。インストールします…" && \
	   curl -LsSf https://astral.sh/uv/install.sh | sh)
	@echo "Done. 次に 'make install' を実行してください。"

.PHONY: install
install: ## 依存関係を .venv に同期
	uv sync

.PHONY: venv
venv: install ## 仮想環境をアクティブにしてシェルを開く
	@echo "Activate .venv … (exit で戻ります)" && \
	  bash -c 'source .venv/bin/activate && exec $$SHELL'

.PHONY: pre-commit
pre-commit: ## pre‑commit フックをインストール
	uv run pre-commit install

.PHONY: lint
lint: ## コードの静的解析
	uv run pre-commit run -a && \
	uv run mypy src

# --------------------------------------------------------------
# ローカルアプリ実行
# --------------------------------------------------------------
.PHONY: run-csv
run-csv: ## CSV ダッシュボード (http://localhost:8501)
	$(STREAMLIT_CMD) $(CSV_APP) --server.port 8501

.PHONY: run-markdown
run-markdown: ## Markdown サマライザー (要 OPENAI_API_KEY)
	@if [ -z "$${OPENAI_API_KEY:-}" ]; then \
	  echo "[WARN] OPENAI_API_KEY が未設定です"; fi
	$(STREAMLIT_CMD) $(MD_APP) --server.port 8501

.PHONY: run-shiny
run-shiny: ## Shiny デモ (http://localhost:8080)
	$(SHINY_CMD) $(SHINY_APP) --port 8080

# --------------------------------------------------------------
# Docker
# --------------------------------------------------------------
.PHONY: docker-build
docker-build: ## 本番用 Docker イメージをビルド
	docker build -t $(DOCKER_IMAGE) .

.PHONY: docker-run-csv
docker-run-csv: docker-build ## CSV ダッシュボードを Docker で実行
	docker run --rm -p 8501:8501 $(DOCKER_IMAGE) csv_dashboard

.PHONY: docker-run-markdown
docker-run-markdown: docker-build ## Markdown サマライザー (要 OPENAI_API_KEY)
	docker run --rm -p 8501:8501 -e OPENAI_API_KEY=$$OPENAI_API_KEY $(DOCKER_IMAGE) markdown_summarizer

.PHONY: docker-run-shiny
docker-run-shiny: docker-build ## Shiny デモを Docker で実行
	docker run --rm -p 8080:8080 $(DOCKER_IMAGE)


# --------------------------------------------------------------
# メンテナンス
# --------------------------------------------------------------
.PHONY: clean
clean: ## ビルドキャッシュ・一時ファイル削除
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache \
	       $(shell find . -type f -name '*.py[cod]' -o -name '*.pyo')

# デフォルト
.DEFAULT_GOAL := help
