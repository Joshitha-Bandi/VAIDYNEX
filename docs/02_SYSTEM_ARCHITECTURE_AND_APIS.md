# 🏛️ MediKiosk — System Architecture & API Specifications

**Document Version:** `1.3.0-PROD`  
**Status:** Approved for Implementation  
**SIH Problem Statement ID:** `26047`  
**Primary Standards:** [NRCeS India FHIR R4](https://nrces.in/ndhm/fhir/r4/) | [NHA ABDM Sandbox](https://sandbox.abdm.gov.in/) | [Sarvam AI Platform](https://www.sarvam.ai/) | [Eka Care Developer Platform](https://developer.eka.care/)  

---

## 1. High-Level Technical Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CLIENT PRESENTATION TIER                                   │
├──────────────────────────────────────────────────┬───────────────────────────────────────────────┤
│          PATIENT KIOSK / MOBILE APP              │           DOCTOR CONSULTATION PORTAL          │
│  • Framework: Flutter 3.24 (Android/Web Kiosk)   │  • Framework: Next.js 15 (React 19)           │
│  • State: Riverpod + Code Generation             │  • State: Zustand + TanStack Query            │
│  • Audio: flutter_sound + AudioWorklet Stream    │  • Styling: Tailwind CSS + Radix UI           │
│  • Routing: GoRouter                             │  • Realtime: Supabase WebSocket Client        │
└─────────────────────────┬────────────────────────┴───────────────────────────────┬───────────────┘
                          │                                                        │
                          ▼ (HTTPS / WSS - TLS 1.3)                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   API GATEWAY & ORCHESTRATION TIER                               │
│                                    FastAPI (Python 3.12 Asynchronous)                            │
├──────────────────────────────────────────────────┬───────────────────────────────────────────────┤
│  • Auth Middleware: JWT + ABHA Token Validator   │  • Rate Limiting: Redis Leaky Bucket          │
│  • WebSocket Manager: Bi-directional Audio Feed  │  • Red-Flag Interceptor: Sub-20ms Regex/NLP   │
│  • Orchestration: LangChain Clinical State Tree  │  • FHIR R4 Serializer: NRCeS DocumentBundle   │
└─────────────────────────┬────────────────────────────────────────────────────────┬───────────────┘
                          │                                                        │
                          ▼                                                        ▼
┌──────────────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│            SOVEREIGN AI SERVICE TIER             │    │       NATIONAL HEALTHCARE GATEWAY        │
│         (Sarvam AI Sovereign Platform)           │    │       (Eka Care ABDM & NHA NHCX)         │
├──────────────────────────────────────────────────┤    ├──────────────────────────────────────────┤
│ • Saaras v3 (Speech-to-Text: 23 Languages)       │    │ • M1: ABHA Creation & Scan & Share       │
│ • Bulbul v3 (Text-to-Speech: 11 Languages)       │    │ • NHCX: CoverageEligibilityRequest (FHIR)│
│ • Sarvam Vision (3B Multimodal VLM: 23 Langs)    │    │ • M2 (HIP): Care Context FHIR Linking    │
│ • Sarvam Translate (Medical Translation)         │    │ • M3 (HIU): Longitudinal Record Fetch    │
└──────────────────────────────────────────────────┘    └──────────────────────────────────────────┘
                          │                                                        │
                          └────────────────────────┬───────────────────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────────┐
                                │             PERSISTENCE TIER             │
                                │         Supabase Managed PostgreSQL      │
                                ├──────────────────────────────────────────┤
                                │ • PostgreSQL 16 with RLS Enabled         │
                                │ • PostGIS (Geographic Hospital Mapping)  │
                                │ • Encrypted Storage Buckets (Scans)      │
                                │ • pgvector (Clinical Semantic Search)    │
                                └──────────────────────────────────────────┘
```

---

## 2. Component-by-Component Specifications

### 2.1 Flutter Kiosk Client (`/kiosk_app`)
* **State Management:** Riverpod 2.x with `@riverpod` code generation.
* **Navigation:** `go_router` declarative routing with deep-linking support for ABHA QR intent.
* **Audio Capture:** `record` and `flutter_sound` configured for $16\text{ kHz}$ mono linear PCM audio streaming.
* **Camera Module:** `camera` plugin with hardware flash control, auto-cropping, and CLAHE contrast preprocessing.
* **Local Persistence:** `hive_flutter` encrypted local box for offline intake resilience.

### 2.2 Doctor Consultation Portal (`/doctor_portal`)
* **Framework:** Next.js 15 (App Router, Server Components).
* **UI & Styling:** Tailwind CSS, Shadcn UI, Radix Primitives, Lucide Icons.
* **Real-time Engine:** `@supabase/supabase-js` subscribing to `encounters` table changes via PostgreSQL Change Data Capture (CDC).
* **Export Engine:** Native `@react-pdf/renderer` for instant prescription printing and PDF sharing.

### 2.3 FastAPI Clinical Gateway (`/backend`)
* **Runtime:** Python 3.12, Uvicorn ASGI with Gunicorn process manager.
* **Data Validation:** Pydantic v2 schemas for strict JSON schema enforcement.
* **State Machine:** LangGraph / Finite State Machine constraining symptom exploration trees.
* **ABDM Standard:** `fhir.resources` Python package generating validated NRCeS HL7 FHIR R4 DocumentBundles.
* **Sarvam Python SDK Usage:**
  ```python
  from sarvamai import SarvamAI
  import os

  client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

  # Saaras v3 STT
  stt_response = client.speech_to_text.transcribe(
      file=audio_file,
      model="saaras:v3",
      language_code="hi-IN"
  )
  ```

---

## 3. Comprehensive REST & WebSocket API Specifications

### 3.1 Authentication & ABHA Identification

#### `POST /api/v1/auth/abha/scan-and-share`
Initiates patient session via ABHA Scan & Share QR code.

* **Request Body:**
```json
{
  "facility_id": "8f9c1e2b-4a3d-4c5e-8b1a-0e9f8d7c6b5a",
  "department_id": "ayush-kayachikitsa-01",
  "qr_payload": "{\"hidn\":\"91-4829-1029-4821\",\"name\":\"Ramesh Chandra\",\"gender\":\"M\",\"dob\":\"1974-05-12\",\"mobile\":\"9876543210\"}"
}
```

* **Response (`200 OK`):**
```json
{
  "status": "SUCCESS",
  "encounter_id": "enc_9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
  "token_number": "AYUSH-042",
  "patient": {
    "abha_number": "91-4829-1029-4821",
    "full_name": "Ramesh Chandra",
    "gender": "MALE",
    "age": 52,
    "primary_language": "Hindi"
  },
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 3.2 NHCX Coverage Eligibility & Scheme Verification

#### `POST /api/v1/insurance/coverage-eligibility/check`
Verifies patient entitlements under PM-JAY and state health schemes via NRCeS FHIR `CoverageEligibilityRequest`.

* **Request Body:**
```json
{
  "encounter_id": "enc_9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
  "abha_number": "91-4829-1029-4821",
  "facility_id": "IN0110000142"
}
```

* **Response (`200 OK`):**
```json
{
  "status": "SUCCESS",
  "eligibility_response": {
    "outcome": "complete",
    "insurance_plan": "Ayushman Bharat PM-JAY",
    "benefit_balance": 500000.0,
    "currency": "INR",
    "covered_services": [
      "FREE_OPD_CONSULTATION",
      "ESSENTIAL_AYURVEDIC_MEDICINES",
      "BIOCHEMICAL_LAB_INVESTIGATIONS"
    ],
    "badge": "PM-JAY Eligible"
  }
}
```

---

### 3.3 Real-time Conversational Intake WebSocket

#### `WS /api/v1/intake/audio-stream`
Bi-directional real-time speech stream connected to Sarvam Saaras v3 ([Sarvam AI STT](https://www.sarvam.ai/)).

* **Query Parameters:** `encounter_id={UUID}&language={iso_code}&mode={ALLOPATHIC|AYUSH}`
* **Client Audio Frame (Binary / JSON):**
```json
{
  "event": "AUDIO_CHUNK",
  "mime_type": "audio/pcm;rate=16000",
  "data_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA..."
}
```

* **Server Response Frame (JSON):**
```json
{
  "event": "TRANSCRIPTION_DELTA",
  "transcription": "mujhe 3 din se tez bukhar hai",
  "is_final": true,
  "detected_symptom": "FEVER",
  "clinical_state": "HPI_ONSET_PROBING",
  "next_prompt": {
    "text": "Kya aapko thand lag kar bukhar aa raha hai?",
    "audio_url": "https://storage.medikiosk.gov.in/audio/prompts/prompt_094.wav",
    "touch_options": ["Haan, thand lagti hai", "Nahi, sirf garmi lagti hai", "Paseena aata hai"]
  }
}
```

---

### 3.4 Document Digitization (Sarvam Vision 3B VLM)

#### `POST /api/v1/documents/digitize`
Uploads and parses paper prescriptions or diagnostic reports ([Sarvam Document AI](https://www.sarvam.ai/apis/document-digitisation)).

* **Request (Multipart Form Data):**
  * `encounter_id`: `UUID`
  * `document_type`: `PRESCRIPTION | LAB_REPORT | DISCHARGE_SUMMARY`
  * `image_file`: Binary file payload

* **Response (`200 OK`):**
```json
{
  "success": true,
  "document_id": "doc_3a2b1c0d-9e8f-7a6b-5c4d-3e2f1a0b9c8d",
  "vlm_model": "sarvam-doc-digitisation-3b",
  "extracted_entities": {
    "medications": [
      {
        "brand_name": "Telma 40",
        "generic_name": "Telmisartan",
        "strength": "40mg",
        "dosage": "1-0-0",
        "duration": "30 days"
      },
      {
        "brand_name": "Rasnadi Guggulu",
        "generic_name": "Polyherbal Ayush Formulation",
        "strength": "500mg",
        "dosage": "2 tabs BD",
        "duration": "15 days"
      }
    ],
    "lab_observations": [
      {
        "test_name": "Serum Uric Acid",
        "observed_value": 7.8,
        "unit": "mg/dL",
        "reference_range": "3.5 - 7.2",
        "flag": "HIGH"
      }
    ]
  },
  "formatted_markdown": "### Digitized Prescription\n- **Telma 40 (Telmisartan 40mg)**: 1 Tab OD Morning (30 Days)\n- **Rasnadi Guggulu**: 2 Tabs BD (15 Days)\n- **Serum Uric Acid**: 7.8 mg/dL *(HIGH)*"
}
```

---

### 3.5 Eka Care ABDM Longitudinal Health Record Retrieval (Milestone 3 - HIU)

#### `POST /api/v1/abdm/records/fetch-past`
Retrieves prior verified clinical encounters from national ABDM health lockers ([Eka Care M3 User Guide](https://developer.eka.care/user-guides/get-started)).

* **Request Body:**
```json
{
  "encounter_id": "enc_9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
  "patient_abha": "91-4829-1029-4821",
  "consent_artefact_id": "consent_81e9f02a-4c3d-2e1b"
}
```

* **Response (`200 OK`):**
```json
{
  "status": "SUCCESS",
  "care_contexts_retrieved": 3,
  "records": [
    {
      "facility_name": "AIIMS New Delhi",
      "encounter_date": "2025-11-10",
      "diagnosis": "Essential Hypertension",
      "prescribed_meds": ["Amlodipine 5mg OD"]
    }
  ]
}
```
