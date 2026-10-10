from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class SystemType(str, Enum):
    ALLOPATHIC = "ALLOPATHIC"
    AYURVEDIC = "AYURVEDIC"
    HYBRID = "HYBRID"

class TriagePriority(str, Enum):
    ROUTINE = "ROUTINE"
    PRIORITY = "PRIORITY"
    EMERGENCY_RED = "EMERGENCY_RED"

class ABHAVerifyRequest(BaseModel):
    abha_number: Optional[str] = None
    abha_address: Optional[str] = None
    qr_payload: Optional[str] = None

class PatientProfile(BaseModel):
    patient_id: str
    abha_number: str
    abha_address: str
    full_name: str
    gender: Gender
    year_of_birth: int
    address: Dict[str, str] = {}
    pmjay_eligible: bool = True

class CoverageEligibilityCheckRequest(BaseModel):
    patient_id: str
    abha_number: str
    scheme_code: str = "PMJAY"

class CoverageEligibilityResponse(BaseModel):
    eligible: bool
    scheme_name: str
    coverage_amount_inr: float
    beneficiary_id: str
    status: str
    message: str

class ChatMessage(BaseModel):
    role: str  # "patient" or "system"
    content: str
    language: str = "hi-IN"

class IntakeChatRequest(BaseModel):
    encounter_id: str
    patient_id: str
    system_type: SystemType = SystemType.HYBRID
    language: str = "hi-IN"
    messages: List[ChatMessage] = []
    current_input: str

class RedFlagAlert(BaseModel):
    is_triggered: bool
    trigger_symptoms: List[str] = []
    recommended_action: str = "PROCEED_WITH_INTAKE"
    latency_ms: float = 12.5

class IntakeChatResponse(BaseModel):
    reply_text: str
    audio_tts_url: Optional[str] = None
    suggested_options: List[str] = []
    step_completed: bool = False
    red_flag: RedFlagAlert
    collected_data: Dict[str, Any] = {}

class OCRRequest(BaseModel):
    encounter_id: str
    image_base64: Optional[str] = None
    document_type: str = "PRESCRIPTION"

class ExtractedMedication(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str

class ExtractedLabResult(BaseModel):
    test_name: str
    value: str
    unit: str
    reference_range: str
    is_abnormal: bool

class OCRResponse(BaseModel):
    document_id: str
    medications: List[ExtractedMedication] = []
    lab_results: List[ExtractedLabResult] = []
    raw_text: str
    confidence_score: float = 0.94

class SoapNote(BaseModel):
    encounter_id: Optional[str] = None
    subjective: str
    objective: str
    assessment: str
    plan: str
    critical_alerts: List[str] = []
    dashavidha_summary: Optional[Dict[str, str]] = None
    dashavidha_matrix: Optional[Dict[str, str]] = None
    pmjay_status: str = "Active (₹5,00,000 Annual Coverage)"
    triage_priority: TriagePriority = TriagePriority.ROUTINE

class EncounterQueueItem(BaseModel):
    encounter_id: str
    token_number: str
    patient_name: str
    age: int
    gender: Gender
    chief_complaint: str
    triage_priority: TriagePriority
    pmjay_eligible: bool
    system_type: SystemType
    created_at: str
    status: str  # "WAITING", "IN_CONSULTATION", "COMPLETED"
