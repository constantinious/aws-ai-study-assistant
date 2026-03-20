"""
Ingestion pipeline: download PDFs from S3, chunk them, embed with Bedrock Titan,
upsert into Pinecone.

Usage:
    python -m scripts.ingest

Prerequisites:
    - AWS credentials configured
    - PINECONE_SECRET_NAME env var pointing to a valid Secrets Manager secret
    - S3 docs bucket populated (make upload-docs)
    - Pinecone index exists (run scripts/create_index.py first)
"""

import hashlib
import logging
import os
import re
import sys
from io import BytesIO

import boto3
from pypdf import PdfReader

# Allow running from backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings  # noqa: E402
from app.models.domain import ExamDomain  # noqa: E402
from app.services.vector_store import upsert_chunks  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CHUNK_SIZE = 512       # tokens approximated as words
CHUNK_OVERLAP = 80     # ~15% overlap

# Map S3 prefixes to exam domains
PREFIX_DOMAIN_MAP: dict[str, ExamDomain] = {
    "whitepapers/ai-ml-fundamentals": ExamDomain.AI_ML_FUNDAMENTALS,
    "whitepapers/generative-ai": ExamDomain.GENERATIVE_AI_FUNDAMENTALS,
    "whitepapers/foundation-models": ExamDomain.FOUNDATION_MODELS,
    "whitepapers/responsible-ai": ExamDomain.RESPONSIBLE_AI,
    "whitepapers/security-governance": ExamDomain.SECURITY_GOVERNANCE,
}


def _infer_domain(s3_key: str) -> ExamDomain:
    for prefix, domain in PREFIX_DOMAIN_MAP.items():
        if s3_key.startswith(prefix):
            return domain
    # Default to foundation models if no prefix matches
    return ExamDomain.FOUNDATION_MODELS


def _chunk_text(text: str) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 50:  # skip tiny fragments
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _extract_text_from_pdf(pdf_bytes: bytes) -> list[tuple[str, int]]:
    """Return list of (page_text, page_number) tuples."""
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            pages.append((text, i + 1))
    return pages


def ingest_bucket(bucket_name: str) -> None:
    s3 = boto3.client("s3", region_name=settings.aws_region)
    paginator = s3.get_paginator("list_objects_v2")

    total_chunks = 0

    for page in paginator.paginate(Bucket=bucket_name, Prefix="whitepapers/"):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.lower().endswith(".pdf"):
                continue

            logger.info("Processing s3://%s/%s", bucket_name, key)
            response = s3.get_object(Bucket=bucket_name, Key=key)
            pdf_bytes = response["Body"].read()

            domain = _infer_domain(key)
            pages = _extract_text_from_pdf(pdf_bytes)

            chunks = []
            for page_text, page_num in pages:
                for chunk_text in _chunk_text(page_text):
                    chunk_id = hashlib.sha256(f"{key}:{page_num}:{chunk_text[:50]}".encode()).hexdigest()
                    chunks.append(
                        {
                            "id": chunk_id,
                            "text": chunk_text,
                            "source": f"s3://{bucket_name}/{key}#page={page_num}",
                            "domain": domain.value,
                            "page": page_num,
                        }
                    )

            if chunks:
                count = upsert_chunks(chunks)
                total_chunks += count
                logger.info("Upserted %d chunks from %s (domain=%s)", count, key, domain.value)

    logger.info("Ingestion complete. Total chunks upserted: %d", total_chunks)


if __name__ == "__main__":
    bucket = os.environ.get(
        "DOCS_BUCKET",
        f"aif-study-docs-{boto3.client('sts').get_caller_identity()['Account']}",
    )
    logger.info("Starting ingestion from bucket: %s", bucket)
    ingest_bucket(bucket)
