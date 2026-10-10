from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import intake, abdm, insurance, documents, doctor, ai, patient

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

@app.get("/")
async def root():
    return {
        "status": "ONLINE",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "abdm": "/api/v1/abdm/abha/verify",
            "insurance": "/api/v1/insurance/coverage-eligibility/check",
            "intake": "/api/v1/intake/chat",
            "documents": "/api/v1/documents/ocr",
            "doctor": "/api/v1/doctor/queue"
        }
    }
