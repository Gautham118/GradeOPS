import requests
from functools import lru_cache
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

bearer_scheme = HTTPBearer()

@lru_cache(maxsize=4)
def fetch_jwks(issuer: str) -> dict:
    url = issuer.rstrip("/") + "/.well-known/jwks.json"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    token = credentials.credentials

    # Try HS256 first (older Supabase projects)
    try:
        return jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
    except JWTError:
        pass

    # Fallback: ES256/RS256 via JWKS (newer Supabase projects)
    try:
        header = jwt.get_unverified_header(token)
        claims = jwt.get_unverified_claims(token)
        issuer  = claims.get("iss")

        if not issuer:
            raise JWTError("Missing issuer in token")

        jwks = fetch_jwks(issuer)
        key  = next(
            (k for k in jwks.get("keys", []) if k.get("kid") == header.get("kid")),
            None
        )
        if not key:
            raise JWTError("No matching JWK found")

        return jwt.decode(
            token,
            key,
            algorithms=[header.get("alg")],
            options={"verify_aud": False}
        )

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")