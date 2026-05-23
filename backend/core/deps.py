# role based access control
from fastapi import Depends, HTTPException
from core.auth import get_current_user
from core.config import supabase_admin

def require_role(*allowed_roles: str):
    async def checker(user: dict = Depends(get_current_user)):
        user_id = user.get("sub")
        profile = supabase_admin.table("profiles").select("role").eq("id", user_id).single().execute()
        if profile.data["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return {**user, "role": profile.data["role"]}
    return checker
