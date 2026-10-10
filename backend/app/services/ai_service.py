import os
import httpx
from typing import List, Optional, Dict, Any
from ..models.schemas import ExtractedMedication, ExtractedLabResult, OCRResponse

class SarvamAIService:
    def __init__(self):
        from ..core.config import settings
        self.api_key = settings.SARVAM_API_KEY or ""
        self.base_url = "https://api.sarvam.ai"

    async def generate_speech(self, text: str, language_code: str = "te-IN") -> Optional[str]:
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        speaker = "kavitha" if language_code in ["te-IN", "ta-IN", "kn-IN"] else "priya"
        payload = {
            "inputs": [text],
            "target_language_code": language_code,
            "speaker": speaker,
            "model": "bulbul:v3"
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(f"{self.base_url}/text-to-speech", headers=headers, json=payload, timeout=12.0)
                if res.status_code == 200:
                    data = res.json()
                    audios = data.get("audios", [])
                    if audios and len(audios) > 0:
                        return audios[0]
        except Exception as e:
            print("Error calling Sarvam TTS:", e)
        return None

    async def translate_text(self, text: str, source_lang: str = "te-IN", target_lang: str = "en-IN") -> Optional[str]:
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "input": text,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
            "speaker_gender": "Male",
            "mode": "formal",
            "model": "mayura:v1"
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(f"{self.base_url}/translate", headers=headers, json=payload, timeout=10.0)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("translated_text")
        except Exception as e:
            print("Error calling Sarvam Translation:", e)
        return None

    async def generate_clinical_completion(self, user_prompt: str, system_prompt: str = "You are an expert physician clinical scribe.") -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sarvam-105b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(f"{self.base_url}/v1/chat/completions", headers=headers, json=payload, timeout=15.0)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print("Error calling Sarvam-105B LLM:", e)
        return None

    def extract_document_ocr(self, document_id: str, doc_type: str = "PRESCRIPTION") -> OCRResponse:
        meds = [
            ExtractedMedication(name="Telmisartan (Telma 40)", dosage="40mg", frequency="1-0-0", duration="30 Days"),
            ExtractedMedication(name="Yograj Guggulu", dosage="500mg", frequency="1-0-1", duration="15 Days"),
            ExtractedMedication(name="Paracetamol", dosage="650mg", frequency="1-1-1 (SOS)", duration="3 Days")
        ]
        labs = [
            ExtractedLabResult(test_name="Serum Uric Acid", value="7.8", unit="mg/dL", reference_range="3.5 - 7.2", is_abnormal=True),
            ExtractedLabResult(test_name="HbA1c", value="6.1", unit="%", reference_range="< 5.7", is_abnormal=True),
            ExtractedLabResult(test_name="Serum Creatinine", value="0.9", unit="mg/dL", reference_range="0.7 - 1.3", is_abnormal=False)
        ]
        raw = "Rx: Tab Telma 40mg OD, Yograj Guggulu 2 tab BD. Serum Uric Acid: 7.8 mg/dL (High). HbA1c: 6.1%."
        return OCRResponse(
            document_id=document_id,
            medications=meds,
            lab_results=labs,
            raw_text=raw,
            confidence_score=0.96
        )

ai_service = SarvamAIService()
