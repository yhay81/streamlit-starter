#!/usr/bin/env bash
set -euo pipefail
case "${1:-$APP}" in       # 1番目の引数 or APP 環境変数
  shiny_demo|"" )
    exec uv run shiny run --host 0.0.0.0 --port 8080 \
         src/shiny_demo/main.py:app ;;
  csv_dashboard )
    exec uv run streamlit run src/csv_dashboard/main.py \
         --server.address=0.0.0.0 ;;
  markdown_summarizer )
    exec uv run streamlit run src/markdown_summarizer/main.py \
         --server.address=0.0.0.0 ;;
  * )
    exec "$@"                # 任意コマンドにフォールバック
esac
