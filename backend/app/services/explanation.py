"""Generate answer explanations using Bedrock Claude Sonnet."""

import json
import logging

from app.config import settings
from app.models.question import AnswerResult, Question, SourceCitation
from app.services.vector_store import retrieve

logger = logging.getLogger(__name__)

_EXPLANATION_PROMPT = """\
A user answered an AWS Certified AI Practitioner (AIF-C01) exam question.

Question: {question_text}

Options:
{options}

User selected: {selected_option}
Correct answer: {correct_option}
User was {correct_wrong}.

Using the AWS documentation context below, write a clear explanation (3-5 sentences) that:
1. States whether the user was correct or incorrect
2. Explains WHY the correct answer is right, citing specific AWS service behaviour or documentation
3. If the user was wrong, briefly explains why their choice is incorrect
4. Helps the user remember the concept for the exam

<context>
{context}
</context>

Respond with ONLY a valid JSON object:
{{
  "explanation": "...",
  "key_concept": "One sentence summarising the core concept to remember"
}}
"""


def _call_bedrock(prompt: str) -> str:
    import boto3

    client = boto3.client("bedrock-runtime", region_name=settings.bedrock_region)
    body = json.dumps(
        {
            "inferenceConfig": {"maxTokens": 512, "temperature": 0.3},
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
        }
    )
    response = client.invoke_model(
        modelId=settings.explanation_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["output"]["message"]["content"][0]["text"]


def generate_explanation(
    question: Question,
    selected_index: int,
    correct_index: int,
) -> AnswerResult:
    correct = selected_index == correct_index
    chunks = retrieve(question.question_text, question.domain, top_k=3)
    context = "\n\n---\n\n".join(c.text for c in chunks if c.text)[:4000]

    options_text = "\n".join(f"  {opt}" for opt in question.options)
    prompt = _EXPLANATION_PROMPT.format(
        question_text=question.question_text,
        options=options_text,
        selected_option=question.options[selected_index],
        correct_option=question.options[correct_index],
        correct_wrong="CORRECT" if correct else "INCORRECT",
        context=context,
    )

    try:
        import re

        raw = _call_bedrock(prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json.loads(match.group()) if match else {}
        explanation = parsed.get("explanation", raw)
    except Exception as exc:
        logger.warning("Explanation generation failed: %s", exc)
        explanation = (
            f"The correct answer is {question.options[correct_index]}. "
            "Please review the relevant AWS documentation for more details."
        )

    citations = [
        SourceCitation(text=c.text[:200], source=c.source)
        for c in chunks
        if c.text
    ]

    return AnswerResult(
        question_id=question.id,
        correct=correct,
        correct_index=correct_index,
        selected_index=selected_index,
        explanation=explanation,
        citations=citations,
    )
