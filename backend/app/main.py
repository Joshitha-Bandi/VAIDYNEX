import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(app_dir)
root_dir = os.path.dirname(backend_dir)
for p in [app_dir, backend_dir, root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

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
    description="MediKiosk Sovereign AI Multimodal Clinical Intake & ABDM Gateway"
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

def _serve_file(filename):
    for candidate in [
        filename,
        os.path.join("public", filename),
        os.path.join(root_dir, filename),
        os.path.join(root_dir, "public", filename)
    ]:
        if os.path.exists(candidate):
            return FileResponse(candidate)
    return HTMLResponse(f"<h1>MediKiosk - {filename}</h1>", status_code=200)

@app.get("/")
async def root():
    return _serve_file("index.html")

@app.get("/doctor")
async def doctor_page():
    return _serve_file("doctor.html")

@app.get("/triage")
async def triage_page():
    return _serve_file("triage.html")

@app.get("/ayush")
async def ayush_page():
    return _serve_file("ayush.html")

@app.get("/admin")
async def admin_page():
    return _serve_file("admin.html")

@app.get("/patient")
async def patient_page():
    return _serve_file("patient.html")

@app.get("/api/health")
async def health():
    return {
        "status": "ONLINE",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
