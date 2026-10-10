try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None
try:
    from .core.config import settings
except (ImportError, ValueError):
    from backend.app.core.config import settings

def get_supabase():
    try:
        if settings.SUPABASE_KEY and len(settings.SUPABASE_KEY) > 10:
            return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        print("Warning: Supabase client init:", e)
    return None

# Module-level singleton
supabase = get_supabase()
