import uuid
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from ..db import supabase

router = APIRouter(prefix="/patient", tags=["Patient Management"])


class PatientRegisterRequest(BaseModel):
    full_name: str = Field(..., example="Ananya Verma")
    age: int = Field(..., example=28)
    gender: str = Field(..., example="Female")
    phone: str = Field(..., example="+91 91234 56789")
    aadhaar: Optional[str] = Field(None, example="8920-1920-4821")
    state: Optional[str] = Field("Telangana", example="Telangana")
    district: Optional[str] = Field("Khammam", example="Khammam")


class PatientResponse(BaseModel):
    id: str
    full_name: str
    age: int
    gender: str
    phone: str
    abha_number: str
    abha_address: str
    aadhaar_masked: str
    pmjay_status: str
    pmjay_id: str
    auth_method: str
    created_at: str


@router.get("/demo-credentials", response_model=List[PatientResponse])
def get_demo_credentials():
    try:
        res = supabase.table("patients").select("*").order("created_at").execute()
        return [PatientResponse(**r) for r in (res.data or [])]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")


@router.post("/register", response_model=PatientResponse)
def register_new_patient(req: PatientRegisterRequest):
    patient_id = f"pat-{uuid.uuid4().hex[:6]}"
    rand_digits = uuid.uuid4().hex[:12]
    abha_number = f"91-{rand_digits[0:4]}-{rand_digits[4:8]}-{rand_digits[8:12]}"
    clean_name = req.full_name.lower().replace(" ", ".")
    abha_address = f"{clean_name}{rand_digits[:3]}@abdm"
    masked_aadhaar = (
        f"XXXX-XXXX-{req.aadhaar[-4:]}"
        if req.aadhaar and len(req.aadhaar) >= 4
        else "XXXX-XXXX-9901"
    )
    pmjay_id = f"PMJAY-TS-{rand_digits[:6]}"
    created_at = datetime.datetime.now().isoformat()

    row = {
        "id": patient_id,
        "full_name": req.full_name,
        "age": req.age,
        "gender": req.gender.upper(),
        "phone": req.phone,
        "abha_number": abha_number,
        "abha_address": abha_address,
        "aadhaar_masked": masked_aadhaar,
        "pmjay_status": "ACTIVE",
        "pmjay_id": pmjay_id,
        "auth_method": "ABHA Kiosk New Registration",
    }
    try:
        supabase.table("patients").insert(row).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

    return PatientResponse(
        id=patient_id,
        full_name=req.full_name,
        age=req.age,
        gender=req.gender,
        phone=req.phone,
        abha_number=abha_number,
        abha_address=abha_address,
        aadhaar_masked=masked_aadhaar,
        pmjay_status="ACTIVE",
        pmjay_id=pmjay_id,
        auth_method="ABHA Kiosk New Registration",
        created_at=created_at,
    )


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_by_id(patient_id: str):
    try:
        res = supabase.table("patients").select("*").eq("id", patient_id).single().execute()
        if res.data:
            return PatientResponse(**res.data)
        raise HTTPException(status_code=404, detail="Patient not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
