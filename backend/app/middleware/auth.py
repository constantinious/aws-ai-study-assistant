"""Cognito JWT verification FastAPI dependency."""

import logging
import time
from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from app.config import settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()


@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    """Fetch and cache Cognito JWKS (cached for the Lambda warm lifetime)."""
    url = (
        f"https://cognito-idp.{settings.aws_region}.amazonaws.com"
        f"/{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )
    response = httpx.get(url, timeout=5)
    response.raise_for_status()
    return {key["kid"]: key for key in response.json()["keys"]}


def _verify_token(token: str) -> dict:
    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")

    keys = _get_jwks()
    if kid not in keys:
        raise JWTError("Unknown key ID")

    public_key = jwk.construct(keys[kid])
    message, encoded_sig = token.rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode())

    if not public_key.verify(message.encode(), decoded_sig):
        raise JWTError("Signature verification failed")

    claims = jwt.get_unverified_claims(token)

    if claims.get("token_use") not in ("access", "id"):
        raise JWTError("Invalid token_use claim")

    if claims.get("exp", 0) < time.time():
        raise JWTError("Token has expired")

    return claims


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """FastAPI dependency — returns the authenticated user_id (Cognito sub)."""
    try:
        claims = _verify_token(credentials.credentials)
        user_id: str = claims["sub"]
        return user_id
    except (JWTError, KeyError, httpx.HTTPError) as exc:
        logger.warning("Auth failure: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
