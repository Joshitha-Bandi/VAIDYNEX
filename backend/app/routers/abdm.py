from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ..models.schemas import ABHAVerifyRequest, PatientProfile
from ..services.abdm_service import abdm_service

router = APIRouter(prefix="/abdm", tags=["ABDM"])

class CreateAbhaRequest(BaseModel):
    full_name: str = Field(..., example="Ananya Verma")
    age: int = Field(..., example=28)
    gender: str = Field(..., example="Female")
    phone: str = Field(..., example="+91 91234 56789")
    aadhaar: Optional[str] = Field(None, example="8920-1920-8901")
    state: Optional[str] = Field("Telangana", example="Telangana")
    district: Optional[str] = Field("Khammam", example="Khammam")
    pincode: Optional[str] = Field("507001", example="507001")

@router.post("/abha/verify", response_model=PatientProfile)
async def verify_abha(req: ABHAVerifyRequest):
    query = req.qr_payload or req.abha_number or "91-4829-1029-4821"
    return abdm_service.verify_abha(query)

@router.post("/registration/create-abha")
async def create_abha_government_standard(req: CreateAbhaRequest) -> Dict[str, Any]:
    return abdm_service.create_nha_abha(
        full_name=req.full_name,
        age=req.age,
        gender=req.gender,
        phone=req.phone,
        aadhaar=req.aadhaar,
        state=req.state or "Telangana",
        district=req.district or "Khammam",
        pincode=req.pincode or "507001"
    )
