import uuid
import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from ..models.schemas import EncounterQueueItem, SoapNote, Gender, TriagePriority, SystemType
from ..services.fhir_service import fhir_service
from ..services.abdm_service import abdm_service
from ..db import supabase

router = APIRouter(prefix="/doctor", tags=["Doctor Portal"])


class NewIntakePayload(BaseModel):
    patient_name: str
    age: int
    gender: str
    identifier_type: str
    identifier_value: str
    symptoms: str
    language: str


class ApproveEncounterPayload(BaseModel):
    encounter_id: str
    patient_id: Optional[str] = "pat-048291"
    patient_name: str
    abha_id: Optional[str] = "91-4829-1029-4821"
    token_number: str
    diagnosis: Optional[str] = "Sandhigata Vata (Knee Osteoarthritis)"
    prescription: Optional[List[Dict[str, Any]]] = None
    soap_note: Optional[Dict[str, Any]] = None


def _row_to_encounter(r: dict) -> EncounterQueueItem:
    return EncounterQueueItem(
        encounter_id=r["id"],
        token_number=r["token_number"],
        patient_name=r["patient_name"],
        age=r["age"],
        gender=Gender.MALE if r["gender"].upper() == "MALE" else (Gender.FEMALE if r["gender"].upper() == "FEMALE" else Gender.OTHER),
        chief_complaint=r.get("chief_complaint") or "General OPD Consultation",
        triage_priority=TriagePriority(r.get("triage_priority", "ROUTINE")),
        pmjay_eligible=r.get("pmjay_eligible", True),
        system_type=SystemType(r.get("system_type", "AYURVEDIC")),
        created_at=str(r.get("created_at", datetime.datetime.now().strftime("%I:%M %p"))),
        status=r.get("status", "WAITING"),
    )


def _row_to_soap(r: dict, encounter_id: str) -> SoapNote:
    return SoapNote(
        encounter_id=encounter_id,
        subjective=r.get("subjective") or "",
        objective=r.get("objective") or "",
        assessment=r.get("assessment") or "",
        plan=r.get("plan") or "",
        critical_alerts=r.get("critical_alerts") or [],
        dashavidha_matrix=r.get("dashavidha_matrix") or {},
        pmjay_status=r.get("pmjay_status") or "Active (₹5,00,000 Annual Coverage)",
        triage_priority=TriagePriority(r.get("triage_priority", "ROUTINE")),
    )


@router.get("/queue", response_model=List[EncounterQueueItem])
async def get_doctor_queue():
    try:
        res = (
            supabase.table("encounters")
            .select("*")
            .order("created_at", desc=False)
            .execute()
        )
        return [_row_to_encounter(r) for r in (res.data or [])]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Queue fetch error: {e}")


@router.get("/token/next")
async def get_next_token():
    try:
        res = supabase.table("encounters").select("token_number").execute()
        rows = res.data or []
        nums = []
        for r in rows:
            tn = r.get("token_number", "").lstrip("#E-").lstrip("#")
            try:
                nums.append(int(tn))
            except ValueError:
                pass
        next_num = (max(nums) + 1) if nums else 1
        token_str = f"#{next_num:03d}"
        return {"token_number": token_str, "next_token_int": next_num}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token error: {e}")


@router.post("/encounter/create")
async def create_new_encounter(payload: NewIntakePayload):
    try:
        res = supabase.table("encounters").select("token_number").execute()
        rows = res.data or []
        nums = []
        for r in rows:
            tn = r.get("token_number", "").lstrip("#E-").lstrip("#")
            try:
                nums.append(int(tn))
            except ValueError:
                pass
        next_num = (max(nums) + 1) if nums else 1
    except Exception:
        next_num = int(uuid.uuid4().hex[:4], 16) % 900 + 100

    token_str = f"#{next_num:03d}"
    enc_id = f"enc-{next_num:04d}"

    enc_row = {
        "id": enc_id,
        "token_number": token_str,
        "patient_name": payload.patient_name,
        "age": payload.age,
        "gender": payload.gender.upper(),
        "chief_complaint": payload.symptoms or "General OPD Consultation",
        "triage_priority": "ROUTINE",
        "pmjay_eligible": True,
        "system_type": "AYURVEDIC",
        "status": "WAITING",
        "language": payload.language,
    }
    soap_row = {
        "encounter_id": enc_id,
        "subjective": f"Patient {payload.patient_name} ({payload.age}Y) registered via MediKiosk ({payload.identifier_type.upper()}: {payload.identifier_value}). Chief Complaint: {payload.symptoms}.",
        "objective": "Clinical Vitals: [To be recorded by consulting physician in OPD chamber]",
        "assessment": "1. Initial OPD Assessment\n2. PM-JAY Cashless OPD Benefit Active",
        "plan": "Clinical consultation pending. Recommended preliminary Ayurvedic Rasayana therapy.",
        "critical_alerts": [],
        "dashavidha_matrix": {"Prakriti": "Vata-Pitta", "Vikriti": "Vata Dominance", "Ahara_Shakti": "Madhyama Agni"},
    }
    try:
        supabase.table("encounters").insert(enc_row).execute()
        supabase.table("soap_notes").insert(soap_row).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encounter creation failed: {e}")

    return {"status": "success", "encounter_id": enc_id, "token_number": token_str, "patient_name": payload.patient_name}


@router.post("/encounter/approve")
async def approve_and_push_encounter(payload: ApproveEncounterPayload):
    try:
        supabase.table("encounters").update({"status": "COMPLETED_APPROVED"}).eq("id", payload.encounter_id).execute()
    except Exception as e:
        print("Encounter status update error:", e)

    try:
        result = abdm_service.push_approved_encounter_to_ndhm(
            encounter_id=payload.encounter_id,
            patient_id=payload.patient_id or "pat-048291",
            patient_name=payload.patient_name,
            abha_id=payload.abha_id or "91-4829-1029-4821",
            token_number=payload.token_number,
            diagnosis=payload.diagnosis or "Clinical Consultation Approved",
            prescription=payload.prescription,
            soap=payload.soap_note,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ABDM push failed: {e}")


@router.get("/transactions")
async def get_all_abdm_transactions():
    try:
        return abdm_service.get_all_abdm_transactions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transactions fetch error: {e}")


@router.get("/encounter/{encounter_id}/soap", response_model=SoapNote)
async def get_soap_note(encounter_id: str):
    try:
        res = (
            supabase.table("soap_notes")
            .select("*")
            .eq("encounter_id", encounter_id)
            .single()
            .execute()
        )
        if res.data:
            return _row_to_soap(res.data, encounter_id)
    except Exception:
        pass

    # Fallback to enc-0042 demo
    try:
        res = supabase.table("soap_notes").select("*").eq("encounter_id", "enc-0042").single().execute()
        if res.data:
            return _row_to_soap(res.data, encounter_id)
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="SOAP note not found")


@router.get("/encounter/{encounter_id}/fhir")
async def get_encounter_fhir(encounter_id: str):
    try:
        res = (
            supabase.table("soap_notes")
            .select("*")
            .eq("encounter_id", encounter_id)
            .single()
            .execute()
        )
        soap_data = res.data if res.data else {}
    except Exception:
        soap_data = {}

    return fhir_service.generate_document_bundle(
        encounter_id=encounter_id,
        patient_id="pat-048291",
        soap_note=soap_data,
    )
