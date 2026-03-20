# AWS AI Practitioner Study Assistant

A RAG-powered adaptive quiz platform for the **AWS Certified AI Practitioner (AIF-C01)** exam. Generates fresh practice questions from official AWS documentation using Amazon Bedrock and adapts to your weak areas.

![Quiz UI](docs/screenshots/quiz.png)

## Features

- **AI-generated questions** — Claude reads your AWS docs and writes contextual exam questions, never the same question twice
- **Adaptive learning** — tracks your accuracy per exam domain and focuses on where you need the most practice
- **Bedrock-powered explanations** — wrong answers trigger a detailed explanation with source citations from AWS documentation
- **5 AIF-C01 domains** covered: AI/ML Fundamentals, Generative AI, Foundation Models, Responsible AI, Security & Governance
- **Progress dashboard** — radar chart and per-domain scorecards to visualise exam readiness
- **Fully serverless** — Lambda + API Gateway + DynamoDB, near-zero cost at low usage

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│              React + TypeScript + Tailwind                  │
│              (CloudFront → S3)                              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS (Cognito JWT)
┌────────────────────────▼────────────────────────────────────┐
│                    API Gateway (HTTP)                        │
│              JWT authoriser → Cognito                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               Lambda — FastAPI (Mangum)                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│   │  Adaptive    │  │  Question    │  │  Progress        │ │
│   │  selector    │  │  generator   │  │  service         │ │
│   └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
└──────────┼─────────────────┼───────────────────┼───────────┘
           │                 │                   │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌────────▼────────┐
    │  DynamoDB   │   │   Bedrock   │   │    Pinecone      │
    │ UserProgress│   │  Claude /   │   │  vector store   │
    │   table     │   │  Titan Embed│   │  (AWS docs RAG) │
    └─────────────┘   └─────────────┘   └─────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Auth | Amazon Cognito (email/password) |
| API | FastAPI on AWS Lambda (Mangum), HTTP API Gateway |
| AI/LLM | AWS Bedrock — Claude Haiku (questions), Claude Sonnet (explanations) |
| Embeddings | Amazon Titan Embed Text v2 (1024 dims) |
| Vector Store | Pinecone serverless (free tier) |
| Database | DynamoDB (pay-per-request) |
| Hosting | S3 + CloudFront |
| IaC | Terraform |
| CI/CD | GitHub Actions (OIDC — no stored credentials) |

## Prerequisites

1. **AWS account** with Bedrock model access enabled:
   - `anthropic.claude-3-haiku-20240307-v1:0`
   - `anthropic.claude-3-sonnet-20240229-v1:0`
   - `amazon.titan-embed-text-v2:0`

   Enable at: AWS Console → Bedrock → Model access → Manage model access

2. **Pinecone account** (free tier) — https://www.pinecone.io
   - Create a project and copy the API key

3. **Terraform state S3 bucket** — create one in `eu-west-1` if you don't have one

4. Tooling: `terraform >= 1.6`, `aws-cli`, `python 3.12`, `node 20`

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/constantinious/aws-ai-study-assistant
cd aws-ai-study-assistant
```

### 2. Deploy infrastructure

```bash
# Update bucket name in terraform/backend.tfvars
echo 'bucket = "your-tf-state-bucket"' >> terraform/backend.tfvars

make tf-init
make tf-apply
```

### 3. Set Pinecone API key

```bash
aws secretsmanager put-secret-value \
  --secret-id aif-study/pinecone-api-key \
  --secret-string '{"api_key":"YOUR_PINECONE_KEY"}'
```

### 4. Create Pinecone index and ingest docs

```bash
cd backend
pip install -r requirements-dev.txt

# Create the vector index (run once)
python -m scripts.create_index

# Download AWS whitepapers into data/whitepapers/<domain>/ subdirectories
# See docs/whitepapers.md for the list of recommended PDFs

# Upload to S3
make upload-docs

# Run ingestion pipeline (embed + upsert to Pinecone)
make ingest
```

### 5. Deploy backend and frontend

```bash
make deploy-backend

# Configure frontend env
cp frontend/.env.example frontend/.env
# Fill in values from: terraform output

make deploy-frontend
```

Visit the CloudFront URL from `terraform output cloudfront_distribution_domain`.

## Local Development

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
cp .env.example .env   # fill in values
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env.local   # fill in values
npm run dev
```

## Running Tests

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

## AWS Whitepapers to Ingest

Place PDFs in the matching `data/whitepapers/<domain>/` subdirectory:

| Directory | Recommended Document |
|---|---|
| `ai-ml-fundamentals/` | AWS Well-Architected ML Lens, SageMaker overview |
| `generative-ai/` | Introduction to Generative AI on AWS |
| `foundation-models/` | Amazon Bedrock User Guide |
| `responsible-ai/` | AWS Responsible AI Whitepaper |
| `security-governance/` | AWS Security Best Practices for AI/ML |

All are freely available at https://aws.amazon.com/whitepapers

## Cost Estimate

| Service | Monthly cost |
|---|---|
| Lambda | ~$0 (free tier) |
| DynamoDB | ~$0 (pay-per-request, low volume) |
| API Gateway | ~$0 (free tier) |
| Bedrock Claude Haiku | ~$0.01 per question |
| Bedrock Claude Sonnet | ~$0.05 per explanation |
| Titan Embed | ~$0.001 per embedding |
| Pinecone | **$0** (free tier) |
| CloudFront + S3 | ~$0 (free tier) |
| Cognito | **$0** (free tier up to 50K MAU) |
| **Total** | **< $5/month** at typical study usage |

## CI/CD

Three GitHub Actions workflows triggered on push to `master`:

- **terraform.yml** — plan on PR, apply on merge
- **backend.yml** — lint, type check, test (80% coverage gate), deploy Lambda
- **frontend.yml** — type check, build, deploy to S3 + CloudFront invalidation

All workflows use OIDC authentication (no long-lived AWS credentials stored).

Required GitHub repository secrets:

```
AWS_ACCOUNT_ID
TF_STATE_BUCKET
VITE_API_URL
VITE_COGNITO_USER_POOL_ID
VITE_COGNITO_APP_CLIENT_ID
FRONTEND_BUCKET
CF_DISTRIBUTION_ID
```
