#!/usr/bin/env bash
set -euo pipefail

APP="${1:-${APP:-}}"

case "$APP" in
  shiny_demo|"")  exec python -m shiny run --host 0.0.0.0 --port 8503 \
                       src/shiny_demo/main.py ;;
  csv_dashboard)  exec python -m streamlit run src/csv_dashboard/main.py \
                       --server.port 8501 --server.address 0.0.0.0 ;;
  markdown_summarizer)
                  exec python -m streamlit run src/markdown_summarizer/main.py \
                       --server.port 8502 --server.address 0.0.0.0 ;;
  *)              exec "$@" ;;
esac
