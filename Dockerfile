# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS runtime

# ---- 1. 非 root ユーザー定義だけしておく（まだ切替えない） ----
RUN adduser --disabled-password --gecos "" streamlit

# ---- 2. 依存関係 ----
WORKDIR /app
COPY pyproject.toml uv.lock* ./

# root 権限で system site‑packages へ
ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --no-editable && uv cache prune -q

# ---- 3. アプリ ----
COPY src/ /app/src/

# ---- 4. 起動スクリプト ----
COPY scripts/launch.sh /usr/local/bin/launch
RUN chmod +x /usr/local/bin/launch

# ---- 5. 権限調整 & 最終ユーザー変更 ----
RUN chown -R streamlit:streamlit /app
USER streamlit

ENV PATH="/home/streamlit/.local/bin:/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app"

EXPOSE 8501 8502 8503

ENTRYPOINT ["launch"]
