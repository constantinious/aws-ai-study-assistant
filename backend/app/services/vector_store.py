"""Pinecone vector store client — retrieval and upsert operations."""

import json
import logging

import boto3
from pinecone import Pinecone

from app.config import settings
from app.models.domain import ExamDomain

logger = logging.getLogger(__name__)

_pinecone_client: Pinecone | None = None


def _get_client() -> Pinecone:
    global _pinecone_client
    if _pinecone_client is None:
        api_key = settings.get_pinecone_api_key()
        _pinecone_client = Pinecone(api_key=api_key)
    return _pinecone_client


def _embed(text: str) -> list[float]:
    """Generate embedding using Amazon Titan Embed v2 via Bedrock."""
    client = boto3.client("bedrock-runtime", region_name=settings.bedrock_region)
    body = json.dumps({"inputText": text, "dimensions": 1024, "normalize": True})
    response = client.invoke_model(
        modelId=settings.embedding_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


class RetrievalResult:
    def __init__(self, text: str, source: str, score: float) -> None:
        self.text = text
        self.source = source
        self.score = score


def retrieve(query: str, domain: ExamDomain, top_k: int = 5) -> list[RetrievalResult]:
    """Retrieve relevant document chunks for a query, filtered by domain."""
    client = _get_client()
    index = client.Index(settings.pinecone_index_name)

    query_vector = _embed(query)

    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter={"domain": {"$eq": domain.value}},
    )

    results = []
    for match in response.get("matches", []):
        metadata = match.get("metadata", {})
        results.append(
            RetrievalResult(
                text=metadata.get("text", ""),
                source=metadata.get("source", "AWS Documentation"),
                score=match.get("score", 0.0),
            )
        )

    logger.info("Retrieved %d chunks for domain=%s query=%r", len(results), domain.value, query[:60])
    return results


def upsert_chunks(chunks: list[dict]) -> int:
    """Upsert document chunks into Pinecone. Used by ingestion script."""
    client = _get_client()
    index = client.Index(settings.pinecone_index_name)

    vectors = []
    for chunk in chunks:
        embedding = _embed(chunk["text"])
        vectors.append(
            {
                "id": chunk["id"],
                "values": embedding,
                "metadata": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "domain": chunk["domain"],
                    "page": chunk.get("page", 0),
                },
            }
        )

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)
        logger.info("Upserted batch %d/%d (%d vectors)", i // batch_size + 1, -(-len(vectors) // batch_size), len(batch))

    return len(vectors)
