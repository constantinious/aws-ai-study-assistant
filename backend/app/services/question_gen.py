"""Generate AIF-C01 exam questions using Bedrock Claude."""

import json
import logging
import re
import uuid

from app.config import settings
from app.models.domain import DOMAIN_METADATA, ExamDomain
from app.models.question import Question
from app.services.vector_store import RetrievalResult, retrieve

logger = logging.getLogger(__name__)

_QUESTION_PROMPT = """\
You are an expert AWS certification exam question writer specialising in the AWS Certified AI Practitioner (AIF-C01) exam.

Your task is to write ONE multiple-choice question for the exam domain: {domain_label}

Use ONLY the following context from official AWS documentation. Do not invent facts.

<context>
{context}
</context>

Requirements:
- The question must test understanding, not just recall
- Include exactly 4 options (A, B, C, D)
- Only one option is correct
- Distractors must be plausible but clearly wrong to someone who understands the topic
- Do not include "All of the above" or "None of the above"

Respond with ONLY a valid JSON object in this exact format:
{{
  "question_text": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct_index": 0,
  "explanation_hint": "Brief reason why the correct answer is right"
}}
"""

_MAX_RETRIES = 2


def _call_bedrock(prompt: str, model_id: str) -> str:
    import boto3

    client = boto3.client("bedrock-runtime", region_name=settings.bedrock_region)
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    response = client.invoke_model(
        modelId=model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


def _parse_question_json(raw: str) -> dict:
    """Extract JSON from Claude response, tolerating markdown code fences."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group())


def _build_context(chunks: list[RetrievalResult]) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {c.source}]\n{c.text}" for c in chunks if c.text
    )


def generate_question(domain: ExamDomain) -> Question:
    """Retrieve relevant context and generate a fresh AIF-C01 question."""
    domain_meta = DOMAIN_METADATA[domain]
    query = f"AWS {domain_meta['label']} exam concepts: {', '.join(domain_meta['topics'][:4])}"

    chunks = retrieve(query, domain, top_k=5)
    if not chunks:
        # Fall back to a broader query without domain filter
        from app.services.vector_store import _embed
        import boto3
        from pinecone import Pinecone
        logger.warning("No chunks found for domain %s — falling back to unfiltered retrieval", domain.value)
        api_key = settings.get_pinecone_api_key()
        pc = Pinecone(api_key=api_key)
        index = pc.Index(settings.pinecone_index_name)
        vec = _embed(query)
        res = index.query(vector=vec, top_k=5, include_metadata=True)
        chunks = [
            RetrievalResult(
                text=m.get("metadata", {}).get("text", ""),
                source=m.get("metadata", {}).get("source", "AWS Documentation"),
                score=m.get("score", 0.0),
            )
            for m in res.get("matches", [])
        ]

    context = _build_context(chunks)
    prompt = _QUESTION_PROMPT.format(
        domain_label=domain_meta["label"],
        context=context[:6000],  # stay within context limits
    )

    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            raw = _call_bedrock(prompt, settings.generation_model_id)
            parsed = _parse_question_json(raw)

            if len(parsed.get("options", [])) != 4:
                raise ValueError("Expected 4 options")
            correct_index = int(parsed["correct_index"])
            if correct_index not in range(4):
                raise ValueError(f"correct_index out of range: {correct_index}")

            from app.services.answer_token import encode_answer_token

            question_id = str(uuid.uuid4())
            token = encode_answer_token(question_id, correct_index)

            return Question(
                id=question_id,
                domain=domain,
                question_text=parsed["question_text"],
                options=parsed["options"],
                answer_token=token,
            )
        except Exception as exc:
            last_error = exc
            logger.warning("Question generation attempt %d failed: %s", attempt + 1, exc)

    raise RuntimeError(f"Failed to generate question after {_MAX_RETRIES + 1} attempts") from last_error
