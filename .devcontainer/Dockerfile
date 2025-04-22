# syntax=docker/dockerfile:1.7
ARG UV_VERSION=latest
ARG UBUNTU_VERSION=latest
###############################################################################
# 0. uv バイナリ専用ステージ (わずか数 MB)                                     #
###############################################################################
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uvbin
#        └────────← ここでタグ展開しておくので後段は変数不要

###############################################################################
# 1. base – OS と共通 CLI                                                      #
###############################################################################
FROM mcr.microsoft.com/devcontainers/base:ubuntu-${UBUNTU_VERSION} AS base
USER root
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential curl ca-certificates zsh git && \
    rm -rf /var/lib/apt/lists/*

# Sheldon
RUN curl -fsSL https://rossmacarthur.github.io/install/crate.sh | \
    bash -s -- --repo rossmacarthur/sheldon --to /usr/local/bin

# uv / uvx をコピー（ステージ名で参照）
COPY --from=uvbin /uv /uvx /usr/local/bin/

RUN chsh -s /usr/bin/zsh vscode

###############################################################################
# 2. deps – Python 依存ライブラリレイヤ                                        #
###############################################################################
FROM base AS deps
USER vscode
WORKDIR /tmp/app
COPY --chown=vscode:vscode pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/home/vscode/.cache/uv,uid=1000,gid=1000 \
    uv sync --locked

###############################################################################
# 3. final – プロジェクト本体                                                  #
###############################################################################
FROM base
USER vscode
WORKDIR /workspace

# 依存レイヤを取り込み
COPY --from=deps /usr/local /usr/local

# アプリケーションのソースをコピー
COPY --chown=vscode:vscode . .

RUN --mount=type=cache,target=/home/vscode/.cache/uv \
    uv sync --locked

# Sheldon プラグイン・zshrc など（省略可）
RUN sheldon -q --non-interactive init --shell zsh && \
    sheldon -q add comp   --github zsh-users/zsh-completions --apply fpath && \
    sheldon -q add sug    --github zsh-users/zsh-autosuggestions            && \
    sheldon -q add syntax --github zsh-users/zsh-syntax-highlighting        && \
    sheldon -q lock && \
    printf '\n# --- Sheldon plugins ---\n'\
'eval "$(sheldon source)"\n'\
'autoload -Uz compinit && compinit\n' >> ~/.zshrc

HEALTHCHECK CMD ["uv", "--version"]
