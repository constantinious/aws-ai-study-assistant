.PHONY: help tf-init tf-plan tf-apply tf-destroy upload-docs ingest \
        backend-dev backend-test backend-build deploy-backend \
        frontend-dev frontend-build deploy-frontend

SHELL := /bin/bash
TF_DIR := terraform
BACKEND_DIR := backend
FRONTEND_DIR := frontend

## ── Help ─────────────────────────────────────────────────────────────────────

help: ## Show available targets
	@awk 'BEGIN{FS=":.*##"} /^[a-zA-Z_-]+:.*##/{printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## ── Terraform ────────────────────────────────────────────────────────────────

tf-init: ## Initialise Terraform (requires backend.tfvars to be configured)
	cd $(TF_DIR) && terraform init -backend-config=backend.tfvars

tf-plan: ## Show Terraform plan
	cd $(TF_DIR) && terraform plan

tf-apply: ## Apply Terraform changes
	cd $(TF_DIR) && terraform apply

tf-destroy: ## Destroy all resources (cost control)
	cd $(TF_DIR) && terraform destroy

## ── Data ingestion ───────────────────────────────────────────────────────────

DOCS_BUCKET ?= $(shell cd $(TF_DIR) && terraform output -raw docs_bucket_name 2>/dev/null)

upload-docs: ## Sync local whitepapers to S3 docs bucket
	aws s3 sync data/whitepapers/ s3://$(DOCS_BUCKET)/whitepapers/ --exclude ".gitkeep"
	@echo "Uploaded docs to s3://$(DOCS_BUCKET)/whitepapers/"

ingest: ## Run Pinecone ingestion pipeline against S3 docs
	cd $(BACKEND_DIR) && .venv/bin/python -m scripts.ingest

## ── Backend ──────────────────────────────────────────────────────────────────

backend-install: ## Install backend dependencies
	cd $(BACKEND_DIR) && pip install -r requirements-dev.txt

backend-dev: ## Run FastAPI dev server locally
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload --port 8000

backend-test: ## Run backend tests with coverage
	cd $(BACKEND_DIR) && pytest --cov=app --cov-report=term-missing --cov-fail-under=80

backend-lint: ## Run ruff + mypy
	cd $(BACKEND_DIR) && ruff check . && mypy app/

backend-build: ## Package Lambda zip
	cd $(BACKEND_DIR) && pip install -r requirements.txt -t dist/ && \
		cp -r app dist/ && \
		cd dist && zip -r ../lambda.zip . && cd ..

LAMBDA_FUNCTION ?= $(shell cd $(TF_DIR) && terraform output -raw lambda_function_name 2>/dev/null)

deploy-backend: backend-build ## Build and deploy Lambda function
	aws lambda update-function-code \
		--function-name $(LAMBDA_FUNCTION) \
		--zip-file fileb://$(BACKEND_DIR)/lambda.zip \
		--architectures arm64

## ── Frontend ─────────────────────────────────────────────────────────────────

frontend-install: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm install

frontend-dev: ## Start Vite dev server
	cd $(FRONTEND_DIR) && npm run dev

frontend-build: ## Build React production bundle
	cd $(FRONTEND_DIR) && npm run build

FRONTEND_BUCKET ?= $(shell cd $(TF_DIR) && terraform output -raw frontend_bucket_name 2>/dev/null)
CF_DISTRIBUTION ?= $(shell cd $(TF_DIR) && terraform output -raw cloudfront_distribution_domain 2>/dev/null)

deploy-frontend: frontend-build ## Build and deploy frontend to S3 + invalidate CloudFront
	aws s3 sync $(FRONTEND_DIR)/dist/ s3://$(FRONTEND_BUCKET)/ --delete
	aws cloudfront create-invalidation \
		--distribution-id $(shell aws cloudfront list-distributions --query "DistributionList.Items[?DomainName=='$(CF_DISTRIBUTION)'].Id" --output text) \
		--paths "/*"
