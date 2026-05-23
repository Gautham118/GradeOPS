from supabase import create_client, Client
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    REDIS_URL: str = "redis://localhost:6379/0"
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

# Admin client (bypasses RLS — only used in workers)
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

# Anon client (respects RLS — used in API routes)
supabase_anon: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
