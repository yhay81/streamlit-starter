#########################
# 0) Backend & Provider
#########################
terraform {
  required_version = "~> 1.11"
  backend "s3" {
    bucket       = "streamlit-suite-tfstate"
    key          = "apprunner/terraform.tfstate"
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
  region = "ap-northeast-1"
  # GitHub では OIDC で AssumeRole、ローカルでは AWS_PROFILE
  profile = var.aws_profile
}

variable "aws_profile" {
  type    = string
  default = "default"
}

#########################
# 1) ECR
#########################
resource "aws_ecr_repository" "app" {
  name                 = "streamlit-suite"
  image_tag_mutability = "MUTABLE"

  lifecycle { prevent_destroy = true }
}

#########################
# 2) AutoScaling = 1
#########################
resource "aws_apprunner_auto_scaling_configuration_version" "one" {
  auto_scaling_configuration_name = "one-instance"
  max_size                        = 1
  min_size                        = 1
  max_concurrency                 = 100
}

###################
# ③ IAM (AppRunner ↔︎ ECR)
###################
data "aws_iam_policy_document" "ecr_pull" {
  # ① リポジトリ固有の Read 権限
  statement {
    sid = "EcrRepoRead"
    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability"
    ]
    resources = [aws_ecr_repository.app.arn]
  }

  # ② トークン取得はリソース指定不可なので "*"
  statement {
    sid       = "EcrAuth"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "apprunner_ecr" {
  name = "AppRunnerECRAccess"
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [{
      Effect : "Allow",
      Principal : { Service : "build.apprunner.amazonaws.com" },
      Action : "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "apprunner_ecr" {
  role   = aws_iam_role.apprunner_ecr.id
  policy = data.aws_iam_policy_document.ecr_pull.json
}

#########################
# 4) Streamlit Apps
#########################
locals {
  app_files = ["csv_dashboard", "markdown_summarizer", "shiny_demo"]
}

# GitHub から渡す値。手元実行時は "latest" で OK
variable "image_tag" {
  type    = string
  default = "latest"
}

variable "openai_api_key" {
  type        = string
  sensitive   = true
  description = "OpenAI API key used by Streamlit apps."
}

resource "aws_apprunner_service" "streamlit" {
  for_each     = toset(local.app_files)
  service_name = "st-${each.key}"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr.arn
    }
    image_repository {
      image_identifier      = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      image_repository_type = "ECR"
      image_configuration {
        port = 8080
        runtime_environment_variables = {
          APP            = each.key
          OPENAI_API_KEY = var.openai_api_key
        }
      }
    }
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/healthz"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.one.arn
}

output "app_urls" {
  value = { for k, s in aws_apprunner_service.streamlit : k => s.service_url }
}

#########################
# 5) EventBridge Scheduler
#########################
variable "resume_cron" {
  # EventBridge Scheduler は UTC ベースなので 23:00 = 翌日 08:00 JST
  default = "cron(0 23 ? * MON-FRI *)"
}
variable "pause_cron" {
  # 12:00 UTC = 21:00 JST
  default = "cron(0 12 ? * MON-FRI *)"
}

data "aws_iam_policy_document" "scheduler_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scheduler" {
  name               = "apprunner-scheduler-role"
  assume_role_policy = data.aws_iam_policy_document.scheduler_trust.json
}

resource "aws_iam_role_policy" "scheduler" {
  role = aws_iam_role.scheduler.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["apprunner:PauseService", "apprunner:ResumeService"]
        Resource = [for s in aws_apprunner_service.streamlit : s.arn]
      }
    ]
  })
}

locals {
  services = { for k, s in aws_apprunner_service.streamlit : k => s.arn }
}

resource "aws_scheduler_schedule" "pause" {
  for_each            = local.services
  name                = "pause-${each.key}"
  schedule_expression = var.pause_cron
  flexible_time_window { mode = "OFF" }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:apprunner:PauseService"
    role_arn = aws_iam_role.scheduler.arn
    input    = jsonencode({ ServiceArn = each.value })
  }
}

resource "aws_scheduler_schedule" "resume" {
  for_each            = local.services
  name                = "resume-${each.key}"
  schedule_expression = var.resume_cron
  flexible_time_window { mode = "OFF" }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:apprunner:ResumeService"
    role_arn = aws_iam_role.scheduler.arn
    input    = jsonencode({ ServiceArn = each.value })
  }
}
