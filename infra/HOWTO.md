# Lightsail Containers & Terraform ― “まっさら AWS” 導入手順書

---

## 0. 前提チェック

| 要素 | 内容 |
|------|------|
| PC   | macOS / Windows / Linux いずれも OK（PowerShell 不可。必ず **Bash** か WSL を使う） |
| ソフト | **Docker Desktop**, **Git**, **AWS CLI v2**, **Terraform ≥ 1.11** |
| AWS アカウント | IAM ユーザー or IAM ロールに「AdministratorAccess」相当の権限があること |

---

## 1. 作業フォルダを用意

```bash
# ★ 任意の場所に clone
git clone https://github.com/your-org/streamlit-suite.git
cd streamlit-suite          # 以後ここが作業ディレクトリ
```

---

## 2. AWS CLI を 1 分で設定 （初回だけ）

```bash
# ① 認証情報を対話で入力（アクセスキー派の場合）
aws configure
# → 指示に従って Access Key / Secret Key / デフォルトリージョン (ap-northeast-1) を入力

# ② OIDC ロールで AssumeRole する環境なら AWS_PROFILE をセット
export AWS_PROFILE=default   # ← 適宜変更
export AWS_REGION=ap-northeast-1
```

---

## 3. tfstate 用 S3 バケットのブートストラップ

> **コピー & ペーストだけ** で完了します。バケットが既にある場合はスキップ。

```bash
export TFSTATE_BUCKET=streamlit-suite-tfstate

aws s3api create-bucket --bucket "$TFSTATE_BUCKET" \
  --region "$AWS_REGION" \
  --create-bucket-configuration LocationConstraint="$AWS_REGION" || true

aws s3api put-bucket-versioning --bucket "$TFSTATE_BUCKET" \
  --versioning-configuration Status=Enabled

aws s3api put-public-access-block --bucket "$TFSTATE_BUCKET" \
  --public-access-block-configuration 'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'

echo "✅  S3 バケット $TFSTATE_BUCKET 作成完了"
```

---

## 4. ECR イメージをビルドしてプッシュ（初回のみ）

```bash
# ① 変数を定義
export IMAGE_TAG=$(git rev-parse --short HEAD)
export ECR_REPO=streamlit-suite
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ② ECR リポジトリが無ければ作成（既にあってもスキップ）
aws ecr describe-repositories --repository-names "$ECR_REPO" 2>/dev/null || \
  aws ecr create-repository --repository-name "$ECR_REPO" --image-tag-mutability MUTABLE

# ③ ECR にログイン
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# ④ ビルド & プッシュ
docker build -t "$ECR_REPO:$IMAGE_TAG" .
docker tag "$ECR_REPO:$IMAGE_TAG" \
  "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"
docker push "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"

echo "✅  ECR プッシュ完了（タグ: $IMAGE_TAG）"
```

---

## 5. OpenAI API キーを環境変数にセット

```bash
export TF_VAR_openai_api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TF_VAR_image_tag="$IMAGE_TAG"
```

> **補足**: `*.auto.tfvars` に書いておく方法もあります（gitignoreされています）。

---

## 6. Terraform を実行

```bash
cd infra
terraform init              # S3 バックエンドを自動検出
terraform apply -auto-approve
```

- 初回は 6〜8 分ほどで完了します。
- 終了時に **`lightsail_endpoint`** として公開 URL が表示されます。

---

## 7. 動作確認

```bash
open https://<lightsail-endpoint>/    # macOS の場合。Windows は start コマンド
```

ブラウザに Streamlit UI が表示されれば成功です。

---

## 8. 更新デプロイ

1. コードを修正
2. `make deploy`（= build → push → terraform plan/apply）

> ECR に push しただけでは Lightsail は再デプロイされません。必ず `terraform apply` を実行してください。

---

## 9. 片付け（削除したいとき）

```bash
cd infra/lightsail
# DeploymentVersion は API が無いので state から外してから destroy
terraform state rm 'aws_lightsail_container_service_deployment_version.current' || true
terraform destroy -auto-approve
aws s3 rb "s3://$TFSTATE_BUCKET" --force   # tfstate バケットも消す場合
```

---

### 完了 🎉

この手順書を上から順に実行すれば、誰でも **Lightsail Container Service + ECR** で Streamlit Suite をデプロイできます。
