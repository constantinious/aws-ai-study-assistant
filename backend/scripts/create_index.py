"""
Create the Pinecone index for document embeddings.

Run once before ingestion:
    python -m scripts.create_index

Titan Embed v2 outputs 1024-dimensional vectors.
"""

import logging
import os
import sys
import time

from pinecone import Pinecone, ServerlessSpec

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DIMENSION = 1024
METRIC = "cosine"
CLOUD = "aws"
REGION = "us-east-1"  # Pinecone free tier is us-east-1


def create_index() -> None:
    api_key = settings.get_pinecone_api_key()
    pc = Pinecone(api_key=api_key)

    existing = [idx.name for idx in pc.list_indexes()]
    if settings.pinecone_index_name in existing:
        logger.info("Index '%s' already exists — skipping creation.", settings.pinecone_index_name)
        return

    logger.info("Creating Pinecone index '%s' (%d dims, %s)...", settings.pinecone_index_name, DIMENSION, METRIC)
    pc.create_index(
        name=settings.pinecone_index_name,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(cloud=CLOUD, region=REGION),
    )

    # Wait until ready
    while not pc.describe_index(settings.pinecone_index_name).status["ready"]:
        logger.info("Waiting for index to be ready...")
        time.sleep(5)

    logger.info("Index '%s' is ready.", settings.pinecone_index_name)


if __name__ == "__main__":
    create_index()
