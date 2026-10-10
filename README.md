# 🏥 MediKiosk — AI-Powered Patient Case-Taking Software
### *Smart India Hackathon (SIH 2026) | Problem Statement ID: 26047*
**Ministry/Department:** All India Institute of Ayurveda (AIIA), Ministry of Ayush  
**Theme:** MedTech / HealthTech / BioTech • **Category:** Software  
**Architecture:** 100% Serverless (Vercel Edge Functions + Supabase PostgreSQL + Sovereign Indic AI)

---

## 📌 Executive Summary & Problem Context

In Indian government tertiary hospitals and apex institutes (e.g., AIIMS, AIIA), outpatient departments (OPDs) register **4,000–10,000 patients daily**. A landmark study published in *BMJ Open (2017)* across 67 countries placed India's average primary-care consultation time at **just over 2 minutes**. 

Within this window, physicians must:
1. Elicit complex medical history across multiple regional languages and dialects.
2. Manually decipher crumpled, handwritten prior paper prescriptions and lab reports.
3. Perform physical examinations, assess Ayurveda's deep *Dashavidha Pariksha* (Prakriti, Vikriti, Agni, Koshtha), formulate diagnoses, and prescribe.

**MediKiosk** solves this "first-mile" clinical bottleneck. It is an autonomous, multimodal, self-service clinical intake platform that captures structured medical history through natural voice conversations in 11+ Indic languages, digitizes paper documents with Vision AI, flags emergency red-flags, and pushes standardized, physician-ready SOAP notes and FHIR bundles to the ABDM ecosystem before the patient enters the consultation room.

---

## 🏛️ The 5+1 Unified Dashboard Suite

| Portal | Route | Target User | Key Capabilities |
| :--- | :--- | :--- | :--- |
| **1. Patient Intake Kiosk** | `/` (`index.html`) | Patients / Attendants | Multilingual voice (Sarvam AI), ABHA OTP/QR login, DPDPA 2023 audio consent, Vision OCR scan, Red-flag STAT triage |
| **2. Doctor Portal** | `/doctor` (`doctor.html`) | OPD Physicians | Real-time queue sync, native mother-tongue audio playback, standardized English SOAP notes, 1-Click ABDM M2 push |
| **3. Emergency Triage Console** | `/triage` (`triage.html`) | ER & Resuscitation Team | Zero-click emergency bypass, Code Blue & Crash Cart alerts, bed routing, real-time hemodynamic monitor |
| **4. AYUSH Portal** | `/ayush` (`ayush.html`) | Ayurvedic Vaidyas / Doctors | *Dashavidha Pariksha* radar charts (Prakriti, Agni, Koshtha), Panchakarma scheduling, NAMASTE & WHO TM-2 coding |
| **5. Patient Health Dashboard** | `/patient` (`patient.html`) | Patients at Home | Personal ID login, past encounter record access, pre-visit symptom check-in, cloud lab record uploader |
| **6. Admin & ABDM Gateway** | `/admin` (`admin.html`) | Hospital Administrators | Live FHIR transaction stream, PM-JAY claim ledger, OPD throughput analytics, national ABDM compliance |

---

## 🧠 Sovereign Indian AI Stack (100% Indigenous)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SOVEREIGN INDIC AI INTEGRATION                                 │
├──────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│    AI MODEL / SERVICE                    │ FUNCTION & CLINICAL ROLE                              │
├──────────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ • Sarvam-105B Indic LLM                  │ Adaptive clinical reasoning, SOCRATES symptom triage, │
│                                          │ SOAP note generation, and pharmacology suggestions.   │
│ • Sarvam Bulbul v3 TTS                   │ High-fidelity Indic voice output in 11 regional       │
│                                          │ languages (Telugu, Tamil, Kannada, Hindi, etc.).      │
│ • Sarvam Mayura v1 Translation           │ Real-time medical translation of Indic vernacular     │
│                                          │ narrative into standardized clinical English.         │
│ • Sarvam Vision 3B VLM                   │ High-accuracy multi-document OCR for handwritten      │
│                                          │ prescriptions and laboratory biomarker extraction.    │
└──────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 🇮🇳 ABDM, FHIR R4 & Regulatory Compliance

* **ABDM Milestone 1 (M1):** Seamless ABHA ID verification, Aadhaar OTP authentication, and Instant ABHA QR card scanning.
* **ABDM Milestone 2 (M2 - HIP):** Automatic linking of digitized clinical encounters to the patient's Care Context and publishing to the Government Health Information Exchange.
* **NRCeS FHIR R4 Compliant:** Generates structured `Bundle` documents containing `Patient`, `Encounter`, `Condition`, `Observation`, and `MedicationRequest` resources.
* **DPDPA 2023 Aligned:** Multilingual, audio-guided, granular consent modal ensuring full legal compliance for low-literacy and elderly populations.

---

## ⚡ Architecture & Deployment

* **Frontend:** Vanilla JavaScript + Tailwind CSS + Lucide Icons (Zero runtime bloat, ultra-lightweight, 60 FPS on low-power kiosk terminals).
* **Backend:** Node.js Serverless Edge Functions deployed on **Vercel** (`/api/v1/`).
* **Cloud Database:** **Supabase Managed PostgreSQL** with Real-Time Replication, Row-Level Security (RLS), and JSONB clinical storage.
* **Dual-Sync Pipeline:** Instant 0ms local caching combined with cloud database synchronization ensures zero latency and continuous operation even with intermittent hospital Wi-Fi.

---

## 🚀 Quickstart & Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/potlasrisharan/medikiosk-sih2026.git
cd medikiosk-sih2026
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Configuration
Create a `.env` file at the root or configure in Vercel:
```env
SUPABASE_URL=https://smydwqouangckxqzskwm.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SARVAM_API_KEY=your_sarvam_api_key
```

### 4. Run Locally
Deploy with Vercel CLI or run any local HTTP server:
```bash
npx vercel dev
# OR
python3 -m http.server 3000
```
Open your browser at `http://localhost:3000/` for the Kiosk or `http://localhost:3000/doctor` for the Doctor Portal.

---

## 👥 Contributors & Acknowledgements

* **Lead Developer:** Potla Sri Sharan
* **Problem Statement:** #26047 — *Patient Case-Taking Software*
* **Target Ministry:** Ministry of Ayush & All India Institute of Ayurveda (AIIA)
* **National Initiative:** Smart India Hackathon (SIH 2026)
