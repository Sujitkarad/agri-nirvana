"""Farmer Authentication & Session Security for Agri Nirvana.

Uses HMAC-SHA256 signed tokens. A production signing secret must be supplied
through the environment; no reusable secret is embedded in source control.
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Optional, Dict, Any

from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel, Field

from backend.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


class SessionRequest(BaseModel):
    farmerId: str = Field(default="farmer_default", min_length=3, max_length=64)
    phone: Optional[str] = Field(default=None, max_length=15)
    name: Optional[str] = Field(default="Farmer", max_length=64)


def _require_jwt_secret() -> str:
    secret = settings.JWT_SECRET.strip()
    if len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured. Set JWT_SECRET to a strong random secret (32+ characters).",
        )
    return secret


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(s: str) -> bytes:
    padding = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + padding)


def create_access_token(user_id: str, extra: Optional[Dict[str, Any]] = None) -> str:
    secret = _require_jwt_secret()
    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + (settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        **(extra or {}),
    }

    header_b64 = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64encode(signature)}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    secret = settings.JWT_SECRET.strip()
    if len(secret) < 32:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        header = json.loads(_b64decode(header_b64).decode("utf-8"))
        if header.get("alg") != settings.JWT_ALGORITHM or header.get("typ") != "JWT":
            return None
        message = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
        actual_sig = _b64decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(_b64decode(payload_b64).decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            return None
        if not payload.get("sub"):
            return None
        return payload
    except Exception:
        return None


def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return decode_access_token(authorization[7:].strip())


def get_current_user_required(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/session")
async def create_farmer_session(req: SessionRequest):
    user_id = req.farmerId.strip() or "farmer_anonymous"
    token = create_access_token(user_id=user_id, extra={"phone": req.phone, "name": req.name})
    return {
        "success": True,
        "token_type": "bearer",
        "access_token": token,
        "user": {"userId": user_id, "phone": req.phone, "name": req.name},
    }


@router.get("/me")
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user_required)):
    return {
        "success": True,
        "userId": current_user.get("sub"),
        "phone": current_user.get("phone"),
        "name": current_user.get("name"),
    }
