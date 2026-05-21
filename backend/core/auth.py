from jose import jwt, JWTError
from fastapi import HTTPException, Header
from core.config import settings

async def get_current_user(authorization: str = Header(...)) -> dict:
    try:
        token = authorization.removeprefix("Bearer ")
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase JWTs have no audience by default
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
