"""
Signed answer tokens — encode the correct answer index in a JWT-like token
so the stateless Lambda never needs to store question state.
"""

import os
import time

from jose import jwt

_SECRET = os.environ.get("ANSWER_TOKEN_SECRET", "dev-secret-change-in-prod")
_ALGORITHM = "HS256"
_TTL_SECONDS = 3600  # 1 hour to answer a question


def encode_answer_token(question_id: str, correct_index: int) -> str:
    payload = {
        "qid": question_id,
        "ans": correct_index,
        "exp": int(time.time()) + _TTL_SECONDS,
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def decode_answer_token(token: str) -> tuple[str, int]:
    """Returns (question_id, correct_index). Raises jose.JWTError on invalid/expired token."""
    payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    return payload["qid"], int(payload["ans"])
