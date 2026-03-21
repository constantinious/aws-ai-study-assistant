terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }

  backend "s3" {
    key    = "aws-ai-study-assistant/terraform.tfstate"
    region = "eu-west-1"
  }
}

# ACM certificates for CloudFront must be in us-east-1
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "aws-ai-study-assistant"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "aws-ai-study-assistant"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
