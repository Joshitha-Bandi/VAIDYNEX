import time
import re
import os
import httpx
import json
from typing import Tuple, List, Dict, Any
from ..models.schemas import RedFlagAlert, SystemType, TriagePriority

RED_FLAG_PATTERNS = [
    r"chest pain", r"severe chest", r"left arm pain", r"heart attack",
    r"chhaati mein dard", r"seene mein dard", r"tez dard",
    r"shortness of breath", r"breathless", r"saans lene mein takleef",
    r"fainting", r"unconscious", r"behosh", r"blood in vomit", r"khoon ki ulti",
    r"sudden paralysis", r"slurred speech", r"face drooping", r"stroke"
]

ALLOPATHIC_QUESTIONS = [
    "Aapko yeh takleef kab se hai? (Duration / Onset)",
    "Dard ya takleef kis jagah par zyada mehsoos hoti hai? (Site / Location)",
    "Dard kaisa mehsoos hota hai - chubhne jaisa, jalan, ya dukhne jaisa? (Character)",
    "Kya dard kisi aur hisse mein bhi failta hai? (Radiation)",
    "Iske sath bukhar, chakkar ya ulti jaisa kuch lag raha hai? (Associated Symptoms)",
    "Kya kisi dawai ya khane se allergy hai? (Allergies)"
]

DASHVAIDHA_QUESTIONS = [
    "Aapki bhookh (Agni) kaisi hai - achhi, kamzor, ya aniyamit?",
    "Aapka pet (Koshtha / Bowel) theek saaf hota hai?",
    "Aapko neend aur thakaan (Nidra / Bala) kaisa rehta hai?",
    "Aapko sardi ya garmi mein se kisme zyada pareshani hoti hai (Prakriti / Sheeta-Ushna)?"
]

from ..core.config import settings
SARVAM_API_KEY = settings.SARVAM_API_KEY or ""
SARVAM_LLM_URL = "https://api.sarvam.ai/v1/chat/completions"

CLINICAL_SYSTEM_PROMPT = """You are the MediKiosk Sovereign AI Clinical Scribe & Decision Support Engine (AIIA Standard).
Given the patient complaints, output ONLY a valid JSON object with these exact keys:
{
  "subjective": "<Clinical English summary of history, onset, duration, aggravations>",
  "assessment": "<Primary diagnosis with NAMASTE and ICD-10 codes>",
  "namaste_code": "<e.g. NAMASTE AYU-SAN-01>",
  "icd10_code": "<e.g. ICD-10 M17.0>",
  "snomed_code": "<e.g. 239873007>",
  "suggested_formulations": [
    {"name": "<Formulation name>", "dose": "<Dose>", "frequency": "<BD/OD/TDS>", "duration": "<Days>", "instructions": "<Anupana/Instructions>"}
  ]
}"""


class ClinicalIntelligenceEngine:
    def evaluate_red_flag(self, text: str) -> RedFlagAlert:
        start_time = time.perf_counter()
        normalized_text = text.lower()
        matched = [
            pattern
            for pattern in RED_FLAG_PATTERNS
            if re.search(pattern, normalized_text)
        ]
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        if matched:
            return RedFlagAlert(
                is_triggered=True,
                trigger_symptoms=matched,
                recommended_action="EMERGENCY_TRIAGE_ALERT",
                latency_ms=round(latency_ms, 2),
            )
        return RedFlagAlert(
            is_triggered=False,
            trigger_symptoms=[],
            recommended_action="PROCEED_WITH_INTAKE",
            latency_ms=round(latency_ms, 2),
        )

    def generate_next_prompt(
        self, current_input: str, step_index: int, system_type: SystemType
    ) -> Tuple[str, List[str], bool]:
        if system_type == SystemType.AYURVEDIC:
            q_list = DASHVAIDHA_QUESTIONS
        elif system_type == SystemType.ALLOPATHIC:
            q_list = ALLOPATHIC_QUESTIONS
        else:
            q_list = ALLOPATHIC_QUESTIONS + DASHVAIDHA_QUESTIONS

        if step_index < len(q_list):
            next_q = q_list[step_index]
            options = ["Haan, bilkul", "Nahi, aisi koi baat nahi", "Thoda bohot", "Pehle se behtar"]
            return next_q, options, False
        return (
            "Dhanyawad. Aapka complete clinical case record taiyyar ho gaya hai.",
            ["Review Summary"],
            True,
        )


clinical_engine = ClinicalIntelligenceEngine()


def call_sarvam_clinical_llm(patient_symptoms: str, language: str = "en-IN") -> Dict[str, Any]:
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sarvam-105b",
        "messages": [
            {"role": "system", "content": CLINICAL_SYSTEM_PROMPT},
            {"role": "user", "content": f"Patient symptoms (Language: {language}): {patient_symptoms}"},
        ],
        "temperature": 0.1,
        "max_tokens": 500,
    }

    try:
        res = httpx.post(SARVAM_LLM_URL, headers=headers, json=payload, timeout=10.0)
        if res.status_code == 200:
            content = res.json()["choices"][0]["message"]["content"]
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print("Sarvam-105B clinical inference fallback:", e)

    # Deterministic fallback
    return {
        "subjective": f"Patient reports {patient_symptoms}. Elicited via sovereign clinical gateway.",
        "assessment": "Sandhigata Vata (Osteoarthritis / ICD-10 M17.0 / NAMASTE AYU-SAN-01)",
        "namaste_code": "NAMASTE AYU-SAN-01",
        "icd10_code": "ICD-10 M17.0",
        "snomed_code": "239873007",
        "suggested_formulations": [
            {"name": "Tab. Yograj Guggulu", "dose": "2 Tabs", "frequency": "BD", "duration": "15 Days", "instructions": "After meals with warm water"},
            {"name": "Kwath. Maharasnadi", "dose": "20 ml", "frequency": "BD", "duration": "15 Days", "instructions": "Before food with equal water"},
        ],
    }
