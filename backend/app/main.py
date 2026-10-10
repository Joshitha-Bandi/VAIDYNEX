import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(app_dir)
root_dir = os.path.dirname(backend_dir)
for p in [app_dir, backend_dir, root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

try:
    from .static_store import get_embedded_file
except (ImportError, ValueError):
    try:
        from app.static_store import get_embedded_file
    except (ImportError, ValueError):
        try:
            from backend.app.static_store import get_embedded_file
        except (ImportError, ValueError):
            def get_embedded_file(filename: str):
                return None

try:
    from .core.config import settings
    from .routers import intake, abdm, insurance, documents, doctor, ai, patient
except (ImportError, ValueError):
    try:
        from app.core.config import settings
        from app.routers import intake, abdm, insurance, documents, doctor, ai, patient
    except (ImportError, ValueError):
        from backend.app.core.config import settings
        from backend.app.routers import intake, abdm, insurance, documents, doctor, ai, patient

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="VAIDYNEX Sovereign AI Multimodal Clinical Intake & ABDM Gateway"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(intake.router, prefix=settings.API_V1_STR)
app.include_router(abdm.router, prefix=settings.API_V1_STR)
app.include_router(insurance.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(doctor.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(patient.router, prefix=settings.API_V1_STR)

def _get_media_type(filename: str) -> str:
    if filename.endswith(".html"):
        return "text/html; charset=utf-8"
    elif filename.endswith(".js"):
        return "application/javascript; charset=utf-8"
    elif filename.endswith(".css"):
        return "text/css; charset=utf-8"
    elif filename.endswith(".ico"):
        return "image/x-icon"
    elif filename.endswith(".svg"):
        return "image/svg+xml"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        return "image/jpeg"
    elif filename.endswith(".png"):
        return "image/png"
    return "text/plain"

def _serve_file(filename: str):
    # 1. Search candidate directories on filesystem
    candidates = [
        os.path.join(app_dir, filename),
        os.path.join(app_dir, "templates", filename),
        os.path.join(backend_dir, filename),
        os.path.join(backend_dir, "app", filename),
        os.path.join(root_dir, filename),
        os.path.join(root_dir, "public", filename),
        os.path.join("/var/task", filename),
        os.path.join("/var/task", "public", filename),
        os.path.join("/var/task", "backend", "app", filename),
        os.path.join(os.getcwd(), filename),
        os.path.join(os.getcwd(), "public", filename),
        filename
    ]
    media_type = _get_media_type(filename)

    for candidate in candidates:
        if os.path.exists(candidate) and os.path.isfile(candidate):
            try:
                with open(candidate, "rb") as f:
                    content = f.read()
                return Response(content=content, media_type=media_type, status_code=200)
            except Exception:
                return FileResponse(candidate)

    # 2. In-memory embedded fallback store
    embedded_bytes = get_embedded_file(filename)
    if embedded_bytes:
        return Response(content=embedded_bytes, media_type=media_type, status_code=200)

    return HTMLResponse(f"<h1>VAIDYNEX - {filename}</h1>", status_code=404)

@app.get("/")
@app.get("/vaidynex")
@app.get("/medikiosk")
@app.get("/kiosk")
@app.get("/index.html")
async def root():
    return _serve_file("index.html")

@app.get("/doctor")
@app.get("/doctor.html")
async def doctor_page():
    return _serve_file("doctor.html")

@app.get("/triage")
@app.get("/triage.html")
async def triage_page():
    return _serve_file("triage.html")

@app.get("/ayush")
@app.get("/ayush.html")
async def ayush_page():
    return _serve_file("ayush.html")

@app.get("/admin")
@app.get("/admin.html")
async def admin_page():
    return _serve_file("admin.html")

@app.get("/patient")
@app.get("/patient.html")
async def patient_page():
    return _serve_file("patient.html")

@app.get("/favicon.ico")
async def favicon():
    return _serve_file("favicon.ico")

@app.get("/favicon.svg")
async def favicon_svg():
    return _serve_file("favicon.svg")

@app.get("/supabase-client.js")
async def supabase_js():
    return _serve_file("supabase-client.js")

@app.get("/logo.jpg")
@app.get("/assets/logo.jpg")
async def logo_jpg():
    return _serve_file("logo.jpg")

@app.get("/api/health")
async def health():
    return {
        "status": "ONLINE",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
