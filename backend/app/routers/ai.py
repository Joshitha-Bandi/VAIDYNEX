from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["Sarvam & Clinical AI"])

class TTSRequest(BaseModel):
    text: str
    language_code: str = "te-IN"

class TTSResponse(BaseModel):
    audio_base64: Optional[str] = None
    language_code: str
    engine: str = "Sarvam Bulbul v3"

class TranslateRequest(BaseModel):
    text: str
    source_language: str = "te-IN"
    target_language: str = "en-IN"

class TranslateResponse(BaseModel):
    translated_text: Optional[str] = None
    source_language: str
    target_language: str
    engine: str = "Sarvam Mayura v1"

class ScribeRequest(BaseModel):
    symptoms: Optional[str] = None
    transcript: Optional[str] = None
    language: Optional[str] = "en-IN"
    patient_id: Optional[str] = None

class ScribeResponse(BaseModel):
    plan: str
    suggested_formulations: List[Dict[str, str]]

@router.post("/tts", response_model=TTSResponse)
async def get_sarvam_tts(req: TTSRequest):
    audio = await ai_service.generate_speech(req.text, req.language_code)
    return TTSResponse(audio_base64=audio, language_code=req.language_code)

@router.post("/translate", response_model=TranslateResponse)
async def get_sarvam_translation(req: TranslateRequest):
    translated = await ai_service.translate_text(req.text, req.source_language, req.target_language)
    return TranslateResponse(translated_text=translated, source_language=req.source_language, target_language=req.target_language)

@router.post("/scribe", response_model=ScribeResponse)
async def get_clinical_scribe(req: ScribeRequest):
    symptom_text = req.symptoms or req.transcript or "General OPD Consultation"
    lower = symptom_text.lower()
    
    if "chest" in lower or "cardiac" in lower or "heart" in lower or "ఛాతీ" in lower:
        return ScribeResponse(
            plan="STAT Resuscitation Protocol: Immediate 12-lead ECG, continuous multiparameter telemetry, dual antiplatelet loading (Aspirin 325mg + Clopidogrel 300mg), sublingual nitroglycerin, high-flow O2 via NRBM.",
            suggested_formulations=[
                {"name": "Tab. Aspirin 325mg (Chewable)", "dose": "325 mg", "freq": "STAT", "dur": "Single Dose", "inst": "Chew immediately"},
                {"name": "Tab. Clopidogrel 300mg", "dose": "300 mg", "freq": "STAT", "dur": "Single Dose", "inst": "Take with water"},
                {"name": "Sorbitrate 5mg (Sublingual)", "dose": "5 mg", "freq": "SOS", "dur": "Every 5 mins up to 3 doses", "inst": "Keep under tongue"}
            ]
        )
    elif "stomach" in lower or "acid" in lower or "reflux" in lower or "కడుపు" in lower:
        return ScribeResponse(
            plan="Acid Peptic Disorder / Amlapitta Regimen: Proton pump inhibitor therapy, mucosal cytoprotection, dietary lifestyle modification (avoid spicy/fermented food, small frequent meals).",
            suggested_formulations=[
                {"name": "Cap. Pantoprazole 40mg", "dose": "40 mg", "freq": "OD", "dur": "14 Days", "inst": "30 mins before breakfast"},
                {"name": "Syp. Sucralfate 10ml", "dose": "10 ml", "freq": "TDS", "dur": "7 Days", "inst": "1 hr before meals"},
                {"name": "Tab. Avipattikar Churna", "dose": "3 grams", "freq": "BD", "dur": "15 Days", "inst": "With warm water before food"}
            ]
        )
    elif "fever" in lower or "chills" in lower or "జ్వరం" in lower:
        return ScribeResponse(
            plan="Acute Febrile Illness / Jwara Protocol: Antipyretic therapy, aggressive oral hydration with ORS, complete blood count & peripheral smear monitoring, tepid sponging.",
            suggested_formulations=[
                {"name": "Tab. Paracetamol 650mg", "dose": "650 mg", "freq": "TDS (8hrly)", "dur": "5 Days", "inst": "After meals"},
                {"name": "Oral Rehydration Salts (ORS)", "dose": "1 Sachet in 1L water", "freq": "Ad libitum", "dur": "5 Days", "inst": "Maintain hydration"},
                {"name": "Syp. Giloy Kwath", "dose": "20 ml", "freq": "BD", "dur": "7 Days", "inst": "Immunity & platelet booster"}
            ]
        )
    else:
        return ScribeResponse(
            plan="Sandhigata Vata (Osteoarthritis) Prescriptive Plan: Ayurvedic chondro-protective formulation, topical anti-inflammatory taila, quadriceps strengthening physiotherapy.",
            suggested_formulations=[
                {"name": "Tab. Yograj Guggulu", "dose": "2 Tabs", "freq": "BD", "dur": "15 Days", "inst": "After meals with warm water"},
                {"name": "Syp. Maharasnadi Kwatha", "dose": "20 ml", "freq": "BD", "dur": "15 Days", "inst": "Before meals with equal water"},
                {"name": "Mahanarayana Taila (Local)", "dose": "10 ml", "freq": "BD", "dur": "30 Days", "inst": "Local application on knees"}
            ]
        )

class LLMProxyRequest(BaseModel):
    model: str = "sarvam-105b"
    messages: List[Dict[str, str]]
    max_tokens: int = 1024
    temperature: float = 0.1
    response_format: Optional[Dict[str, str]] = None

@router.post("/llm-proxy")
async def get_sarvam_llm_proxy(req: LLMProxyRequest):
    import os, httpx, json
    from fastapi import HTTPException
    from ..core.config import settings
    
    SARVAM_KEY = settings.SARVAM_API_KEY or ""
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if req.model.startswith("openai/"):
        req.model = "sarvam-105b"

    headers["api-subscription-key"] = SARVAM_KEY
    headers["Authorization"] = f"Bearer {SARVAM_KEY}"
    url = "https://api.sarvam.ai/v1/chat/completions"
        
    payload = {
        "model": req.model,
        "messages": req.messages,
        "max_tokens": req.max_tokens,
        "temperature": req.temperature
    }
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload, timeout=15.0)
            res.raise_for_status()
            return res.json()
    except Exception as e:
        print("LLM Proxy error:", e)
        mock_content = {
            "english_translation": "Fallback: Symptoms noted.",
            "is_emergency": False,
            "clinical_assessment": "Standard clinical observation due to AI timeout.",
            "planSummary": "Proceed with standard care protocol.",
            "dashavidha": {"prakriti": "Vata-Kapha", "agni": "Manda Agni", "koshtha": "Madhyama", "vikriti": "Dosha Dusti"},
            "aiSuggestions": [],
            "activePrescription": []
        }
        return {
            "choices": [
                {"message": {"content": json.dumps(mock_content)}}
            ]
        }
