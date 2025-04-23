# infra README – Streamlit Suite Infrastructure

このドキュメントは **AWS App Runner で Streamlit Suite を運用するための IaC**（Terraform＋Makefile）だけにフォーカスした説明です。
アプリの使い方は `apps/README.md` を参照してください。

---

## 1 概要

| 項目 | 内容 |
|------|------|
| **IaC** | Terraform 1.11（S3 backend + `use_lockfile=true`） |
| **コンテナレジストリ** | ECR `streamlit‑suite`（タグ: `latest` と Git SHA） |
| **実行基盤** | AWS App Runner 3 サービス |
| **自動起動/停止** | EventBridge Scheduler で平日 08‑21 JST のみ稼働 |
| **CI/CD** | GitHub Actions または `infra/Makefile` |

---

## 2 ディレクトリ構成

```text
.
├── Dockerfile          # プロジェクトルートに配置
├── apps/               # Streamlit / Shiny アプリ本体
└── infra/              # ├── main.tf / variables.tf … Terraform
                        # └── Makefile              … デプロイ補助
```

> **Makefile は `infra/Makefile`** に置きます。
> Docker ビルドコンテキストは 1 つ上のルートに向けています。

---

## 3 前提ツール

| ツール | バージョン例 |
|--------|--------------|
| Docker | 20.10+ |
| AWS CLI | v2 |
| Terraform | 1.11+ |
| Git | 任意（TAG 自動生成で使用） |

初回のみ Terraform 状態ファイル保存用 S3 バケットを手動作成してください:

```bash
aws s3 mb s3://streamlit-suite-tfstate --region ap-northeast-1
aws s3api put-bucket-versioning \
  --bucket streamlit-suite-tfstate \
  --versioning-configuration Status=Enabled
```

---

## 4 Make コマンド早見表

| コマンド | 処理 | 環境変数 |
|----------|------|----------|
| `make build`   | Docker イメージ `latest` と `$(TAG)` をビルド | `TAG` |
| `make login`   | ECR へログイン | `AWS_PROFILE` `AWS_REGION` |
| `make push`    | イメージ 2 タグを ECR に push（`login`,`build` 自動実行） | 同上 |
| `make plan`    | `terraform plan -out plan.tfplan` | `TAG` |
| `make apply`   | 生成済み plan を適用 |  |
| `make deploy`  | **build → push → plan → apply** を一括実行 | 同上 |
| `make destroy` | 全リソース削除 |  |
| `make fmt`     | Terraform ファイルを整形 |  |

既定値:

```text
AWS_PROFILE = default
AWS_REGION  = ap-northeast-1
ECR_REPO    = streamlit-suite
TAG         = $(git rev-parse --short HEAD)
```

例）`AWS_PROFILE=dev TAG=test make deploy`

---

## 5 クイックスタート

```bash
# プロジェクトルートをクローン
git clone https://github.com/<you>/streamlit-suite.git
cd streamlit-suite

# 初回のみ: 状態ファイル用 S3 を作成（上記参照）

# infra ディレクトリへ
cd infra

# ワンライナーでデプロイ
make deploy                # TAG=git SHA, AWS_PROFILE=default

# URL は apply 出力または AWS コンソールで確認
```

---

## 6 CI/CD との統一

GitHub Actions では

1. Docker build (`docker build -t $ECR_URI:$GITHUB_SHA -t …:latest …`)
2. push (`docker push` 2 タグ)
3. `terraform apply -var="image_tag=$GITHUB_SHA"`

を実行し、ローカルの `make deploy` と同一フローを再現します。

---

## 7 変数 (`infra/variables.tf`)

| 変数 | 既定値 | 説明 |
|------|--------|------|
| `aws_profile` | `"default"` | ローカル terraform 実行用 |
| `image_tag` | `"latest"` | App Runner に設定する ECR タグ |
| `resume_cron` | `cron(0 23 ? * MON-FRI *)` | 平日 08:00 JST Resume |
| `pause_cron` | `cron(0 12 ? * MON-FRI *)` | 平日 21:00 JST Pause |

---

## 8 トラブルシューティング

| 症状 | 原因・対処 |
|------|-----------|
| `Health check failed` | Dockerfile が **0.0.0.0:8080** で Listen しているか／ポート番号一致か |
| `ECR image doesn't exist` | push 済みタグと `image_tag` が一致しているか |
| `StateLock` エラー | 別ターミナルで apply が動いていないか／S3 ロックファイル残存 |

---

## 9 リソース削除

```bash
cd infra
make destroy   # or terraform destroy
```

---

© 2025 Streamlit Suite Infra
