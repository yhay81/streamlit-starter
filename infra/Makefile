# ============================================================================
# グローバル設定（環境変数で上書き可）
# ============================================================================
AWS_PROFILE ?= default
AWS_REGION  ?= ap-northeast-1
ECR_REPO    ?= streamlit-suite
TAG         ?= $(shell git -C $(ROOT_DIR) rev-parse --short HEAD)

# 変数派生
ACCOUNT_ID  := $(shell aws sts get-caller-identity  \
                      --profile $(AWS_PROFILE) --query Account --output text)
ECR_URI     := $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO)
ROOT_DIR    := $(strip $(abspath $(CURDIR)/..))

# ============================================================================
# ターゲット
# ============================================================================
.PHONY: login build push plan apply deploy destroy fmt

## 1) ECR ログイン
login:
	@echo "🔑  Logging in to ECR ($(AWS_PROFILE))"
	@aws ecr get-login-password --profile $(AWS_PROFILE) --region $(AWS_REGION) \
	    | docker login --username AWS --password-stdin \
	      $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

## 2) Docker ビルド（latest & TAG）
build:
	@echo "🐳  Docker build: $(TAG)"
	docker build \
		-f $(ROOT_DIR)/Dockerfile \
		-t $(ECR_URI):$(TAG) \
		-t $(ECR_URI):latest \
		$(ROOT_DIR)

## 3) Docker プッシュ
push: login build
	@echo "📤  Pushing images to ECR"
	docker push $(ECR_URI):$(TAG)
	docker push $(ECR_URI):latest

## 4) Terraform plan
plan:
	@echo "📋  Terraform plan"
	terraform init -reconfigure -upgrade -input=false
	terraform plan -input=false -var="image_tag=$(TAG)" -out=plan.tfplan

## 5) Terraform apply
apply:
	@echo "🚀  Terraform apply"
	terraform apply -input=false plan.tfplan

## 6) 一括デプロイ → build / push / plan / apply
deploy: push plan apply
	@echo "✅  Deploy complete!  Tag = $(TAG)"

## 7) statefmt
fmt:
	@terraform fmt -recursive

## 8) 破棄
destroy:
	terraform destroy -var="image_tag=$(TAG)"
