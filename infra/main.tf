#########################
# Lightsail Containers – Streamlit Suite (experimental)
# Replaces App Runner. Reuses existing ECR repo and common variables.
#########################

terraform {
  required_version = "~> 1.11"
  backend "s3" {
    bucket       = "streamlit-suite-tfstate"
    key          = "lightsail/terraform.tfstate"
    region       = "ap-northeast-1"
    use_lockfile = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.90"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-1"
  profile = var.aws_profile
}

#########################
# 0) Variables & Locals
#########################

variable "aws_profile" {
  description = "AWS profile name when running locally"
  type        = string
  default     = "default"
}

variable "image_tag" {
  description = "Docker image tag pushed to ECR"
  type        = string
  default     = "latest"
}

variable "openai_api_key" {
  description = "OpenAI API key used by Streamlit apps"
  type        = string
  sensitive   = true
}

locals {
  apps = {
    csv   = { app_file = "csv_dashboard", port = 8501, path = "/csv" }
    md    = { app_file = "markdown_summarizer", port = 8502, path = "/md" }
    shiny = { app_file = "shiny_demo", port = 8503, path = "/shiny" }
  }

  public_app = "proxy" # 逆プロキシを公開
}

#########################
# 1) ECR (unchanged)
#########################

resource "aws_ecr_repository" "app" {
  name                 = "streamlit-suite"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

resource "aws_ecr_repository" "proxy" {
  name                 = "streamlit-proxy"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

#########################
# 2) IAM – Lightsail ↔︎ ECR (private registry access)
#########################

data "aws_iam_policy_document" "ecr_pull" {
  statement {
    sid = "EcrRepoRead"
    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability"
    ]
    resources = [aws_ecr_repository.app.arn, aws_ecr_repository.proxy.arn]
  }

  statement {
    sid       = "EcrAuth"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "lightsail_ecr" {
  name = "LightsailECRAccess"
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [{
      Effect : "Allow",
      Principal : { Service : "lightsail.amazonaws.com" },
      Action : "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lightsail_ecr" {
  role   = aws_iam_role.lightsail_ecr.id
  policy = data.aws_iam_policy_document.ecr_pull.json
}

#########################
# 3) Lightsail Container Service
#########################

resource "aws_lightsail_container_service" "this" {
  name        = "streamlit-suite"
  power       = "small" # nano|micro|small|medium|large|xlarge xxlarge
  scale       = 1       # number of running containers (1‒20)
  is_disabled = false

  private_registry_access {
    ecr_image_puller_role {
      is_active = true
    }
  }
}

resource "aws_lightsail_container_service_deployment_version" "current" {
  service_name = aws_lightsail_container_service.this.name

  # ---- 1. 逆プロキシ（公開コンテナ） --------------------------
  container {
    container_name = "proxy"
    image          = "${aws_ecr_repository.proxy.repository_url}:${var.image_tag}"
    ports          = { "80" = "HTTP" }
  }

  # ---- 2. 各 Streamlit アプリ ---------------------------------
  dynamic "container" {
    # → each.key  : csv-dashboard
    # → each.value: { app_file = "...", port = ..., path = "..." }
    for_each = local.apps
    content {
      container_name = container.key
      image          = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"

      # Lightsail では “このポートを開く” 宣言が必須
      ports = { tostring(container.value.port) = "HTTP" } # 例: "8501" = "HTTP"

      # Streamlit 起動用の環境変数
      environment = {
        APP                            = container.value.app_file
        OPENAI_API_KEY                 = var.openai_api_key
        STREAMLIT_SERVER_PORT          = tostring(container.value.port)
        STREAMLIT_SERVER_BASE_URL_PATH = container.value.path
      }
    }
  }

  # ---- 3. 公開エンドポイント (逆プロキシ) -----------------------
  public_endpoint {
    container_name = "proxy"
    container_port = 80
    health_check {
      path                = "/"
      healthy_threshold   = 2
      unhealthy_threshold = 2
      interval_seconds    = 30
      timeout_seconds     = 5
      success_codes       = "200-299"
    }
  }
}

#########################
# 4) Outputs
#########################

output "lightsail_endpoint" {
  description = "Public URL for the Streamlit service"
  value       = aws_lightsail_container_service.this.url
}
