# ============================================================================
# 共通 – 変数
# ============================================================================
AWS_PROFILE ?= default
AWS_REGION  ?= ap-northeast-1

# ── Streamlit App（既存）
APP_ECR_REPO ?= streamlit-suite
APP_DOCKERFILE ?= $(ROOT_DIR)/Dockerfile
APP_CONTEXT    ?= $(ROOT_DIR)

# ── Nginx Proxy（新規）
PROXY_ECR_REPO ?= streamlit-proxy
PROXY_DOCKERFILE ?= $(ROOT_DIR)/infra/proxy/Dockerfile
PROXY_CONTEXT    ?= $(ROOT_DIR)/infra/proxy

# Git SHA をタグに利用
TAG ?= $(shell git -C $(ROOT_DIR) rev-parse --short HEAD)

# 便利変数
ACCOUNT_ID := $(shell aws sts get-caller-identity \
	                --profile $(AWS_PROFILE) --query Account --output text)
ECR_URI     = $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
APP_ECR_URI    = $(ECR_URI)/$(APP_ECR_REPO)
PROXY_ECR_URI  = $(ECR_URI)/$(PROXY_ECR_REPO)
ROOT_DIR   := $(strip $(abspath $(CURDIR)/..))

.PHONY: login build build-app build-proxy push push-app push-proxy \
        plan apply deploy deploy-all fmt destroy

# ============================================================================
# 0) ECR ログイン
# ============================================================================
login:
	@echo "🔑  Logging in to ECR ($(AWS_PROFILE))"
	@aws ecr get-login-password --profile $(AWS_PROFILE) --region $(AWS_REGION) \
	    | docker login --username AWS --password-stdin $(ECR_URI)

# ============================================================================
# 1) Docker ビルド
# ============================================================================
build: build-app build-proxy

build-app:
	@echo "🐳  [App] Docker build: $(TAG)"
	docker build --platform linux/amd64 \
		-f $(APP_DOCKERFILE) \
		-t $(APP_ECR_URI):$(TAG) \
		-t $(APP_ECR_URI):latest \
		$(APP_CONTEXT)

build-proxy:
	@echo "🐳  [Proxy] Docker build: $(TAG)"
	docker build --platform linux/amd64 \
		-f $(PROXY_DOCKERFILE) \
		-t $(PROXY_ECR_URI):$(TAG) \
		-t $(PROXY_ECR_URI):latest \
		$(PROXY_CONTEXT)

# ============================================================================
# 2) Docker プッシュ
# ============================================================================
push: push-app push-proxy

push-app: login build-app
	@echo "📤  [App] Pushing images to ECR"
	docker push $(APP_ECR_URI):$(TAG)
	docker push $(APP_ECR_URI):latest

push-proxy: login build-proxy
	@echo "📤  [Proxy] Pushing images to ECR"
	docker push $(PROXY_ECR_URI):$(TAG)
	docker push $(PROXY_ECR_URI):latest

# ============================================================================
# 3) Terraform
# ============================================================================
plan:
	@echo "📋  Terraform plan"
	terraform init -reconfigure -upgrade -input=false
	terraform plan -input=false \
		-var="image_tag=$(TAG)" \
		-out=plan.tfplan

apply:
	@echo "🚀  Terraform apply"
	terraform apply -input=false plan.tfplan

# ============================================================================
# 4) ワンライナー
# ============================================================================
deploy: push plan apply
	@echo "✅  Deploy complete!  Tag = $(TAG)"

deploy-all: login build push plan apply

# ============================================================================
# その他
# ============================================================================
fmt:
	@terraform fmt -recursive

destroy:
	terraform destroy -var="app_image_tag=$(TAG)" -var="proxy_image_tag=$(TAG)"
