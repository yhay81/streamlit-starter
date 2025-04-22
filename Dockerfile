# syntax=docker/dockerfile:1

# ──────────────── 1. ベースイメージ ────────────────
# 「uv + Python3.13 + Debian bookworm‑slim」
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS runtime
#            └─────────────── tag の一例 ─┴───────────
# * 具体的なバージョンを固定する場合は
#   ghcr.io/astral-sh/uv:0.6.11-python3.13-bookworm-slim などにするとなお良い

# ──────────────── 2. 非 root ユーザー ────────────────
RUN adduser --disabled-password --gecos "" streamlit
USER streamlit
WORKDIR /app

# ──────────────── 3. 依存関係レイヤ ────────────────
# まず `pyproject.toml` / `uv.lock` だけコピーしてキャッシュを最大化
COPY --chown=streamlit:streamlit pyproject.toml uv.lock* ./

# system site‑packages にインストール
ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --no-editable    \
    && uv cache prune -q

# ──────────────── 4. アプリケーション ────────────────
COPY --chown=streamlit:streamlit src/ /app/src/

ENV PATH="/home/streamlit/.local/bin:${PATH}"
ENV PYTHONPATH="/app"

EXPOSE 8501 8080
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# ──────────────── 5. 起動コマンド ────────────────
# `uv run` で仮想環境を意識せず実行
COPY scripts/launch.sh /usr/local/bin/launch
ENTRYPOINT ["launch"]
CMD ["shiny_demo"]
