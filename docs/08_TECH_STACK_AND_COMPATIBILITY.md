# 🛠️ MediKiosk — Full Production Tech Stack & Compatibility Specification

**Document Version:** `1.0.0-PROD`  
**Status:** Approved for Implementation  
**SIH Problem Statement ID:** `26047`  
**Target Ministry:** Ministry of Ayush / All India Institute of Ayurveda (AIIA)  
**Primary Standards:** Ayushman Bharat Digital Mission (ABDM) | NRCeS FHIR R4 | NHCX | DPDPA 2023  
**Sovereign AI Foundation:** [Sarvam AI](https://www.sarvam.ai/)  
**ABDM Gateway:** [Eka Care Developer Platform](https://developer.eka.care/)  

---

## 1. High-Level Architecture & Stack Summary

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   MEDIKIOSK COMPLETE TECH STACK                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Kiosk Frontend:       Flutter 3.24 (Clean Architecture + Riverpod + GoRouter + Hive)          │
│ 2. Doctor Web Portal:    Next.js 15 (React 19 + TypeScript 5.5 + Tailwind CSS + Shadcn UI)       │
│ 3. Clinical API Gateway: FastAPI (Python 3.12 Asynchronous + Pydantic v2 + LangGraph)           │
│ 4. Sovereign AI Engine:  Sarvam AI (Saaras v3 STT + Bulbul v3 TTS + Sarvam Vision 3B VLM)       │
│ 5. National Gateways:    Eka Care ABDM Platform (M1, M2, M3) + NHA NHCX (FHIR Coverage Engine)   │
│ 6. Database & Realtime:  Supabase (PostgreSQL 16 + Row Level Security + Realtime WebSockets)     │
│ 7. Cache & DevOps:       Redis 7 Alpine + Docker Compose + GitHub Actions CI/CD                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer-by-Layer Technical Stack

### 2.1 Patient Intake Kiosk (Mobile / Tablet / Kiosk Hardware)
* **Framework:** **Flutter 3.24 (Dart 3.5)** — Stable Channel Only
* **Architecture:** Clean Architecture (`core/`, `features/{data, domain, presentation}`)
* **State Management:** `flutter_riverpod` + `riverpod_annotation` (Code generation via `build_runner`)
* **Navigation:** `go_router` (Declarative routing with deep-link intent handling for ABHA QR)
* **Audio Streaming:** `flutter_sound` + `record` ($16\text{ kHz}$ mono linear PCM audio streaming over WebSockets)
* **Camera & Scanner:** `camera` plugin with hardware flash control, auto-cropping, and CLAHE contrast filters
* **Local Offline Storage:** `hive_flutter` (Encrypted box with AES-256 key for kiosk offline resilience)
* **Secure Storage:** `flutter_secure_storage` (Hardware-backed keystore for local token caching)
* **Typography:** `google_fonts` (Noto Sans / Poppins with regional Indic script support)

### 2.2 Doctor Consultation Portal (Web)
* **Framework:** **Next.js 15 (App Router, React 19, Server Components)**
* **Language:** TypeScript 5.5 (Strict null-safety)
* **Styling & Components:** Tailwind CSS v3.4 + Radix UI + Shadcn UI + Lucide Icons
* **Client State & Caching:** Zustand + TanStack Query v5
* **Real-time Live Sync:** `@supabase/supabase-js` (WebSocket subscription on PostgreSQL Change Data Capture for instant OPD token lighting)
* **Clinical PDF Generation:** `@react-pdf/renderer` (Instant 1-click printable prescription & discharge summaries)

### 2.3 Backend & Clinical Intelligence Gateway
* **Framework:** **FastAPI (Python 3.12)** with Uvicorn ASGI & Gunicorn worker manager
* **Data Validation:** Pydantic v2 (Strict typing and JSON schema validation)
* **Clinical Dialogue Engine:** LangGraph / Finite State Machine (SOCRATES Allopathic & *Dashavidha Pariksha* AYUSH trees)
* **Red-Flag Emergency Interceptor:** Sub-20ms regex & NLP triage filter for acute cardiac/stroke symptoms
* **FHIR Serializer:** `fhir.resources` (Generates validated NRCeS HL7 FHIR R4 DocumentBundles)
* **Cryptography:** `cryptography` (Curve25519 Diffie-Hellman + AES-GCM-256 for ABDM encrypted transfers, HMAC-SHA256 for DPDPA consent)

### 2.4 Sovereign AI Foundation (Sarvam AI India)
* **Official SDK:** `sarvamai` (Python SDK)
* **Speech-to-Text (STT):** **Sarvam Saaras v3** (22 Indian languages + English, noise-robust, code-mixed Hinglish/Tanglish support)
* **Text-to-Speech (TTS):** **Sarvam Bulbul v3** (11 languages, 35+ expressive regional voices for low-literacy audio guidance)
* **Medical Document AI:** **Sarvam Vision (3B Multimodal VLM)** (Multilingual cursive handwritten prescription & multi-column lab report OCR across 23 languages)
* **Medical Translation:** **Sarvam Translate** (Standardizes regional dialect medical terms into clinical terminology)

### 2.5 National Healthcare Ecosystem & ABDM Integration
* **ABDM Gateway:** **Eka Care Developer Platform (`developer.eka.care`)**
  * **Milestone 1 (M1):** ABHA creation, verification, mobile OTP, and QR Scan & Share
  * **Milestone 2 (HIP):** Care Context linking & FHIR health data bundle publishing
  * **Milestone 3 (HIU):** Consent Manager integration & historical health record fetching across Indian hospitals
* **Insurance & Scheme Engine:** **NHA National Health Claims Exchange (NHCX)**
  * **Profile:** NRCeS FHIR R4 `CoverageEligibilityRequest` & `CoverageEligibilityResponse` for real-time PM-JAY (₹5 Lakh coverage) verification

### 2.6 Persistence & Data Layer
* **Database:** **Supabase Managed PostgreSQL 16**
* **Security:** **Row Level Security (RLS)** enabled on all tables (strict multi-tenant hospital isolation)
* **Geospatial Mapping:** PostGIS extension (Hospital and district mapping)
* **Document Storage:** Supabase Encrypted S3 Storage Buckets (Encrypted medical scan storage)
* **Vector Search:** `pgvector` extension (Semantic retrieval on past clinical diagnoses)

### 2.7 In-Memory Cache, DevOps & CI/CD
* **In-Memory Cache:** Redis 7 Alpine (Leaky-bucket rate limiting and active kiosk intake session cache)
* **Containerization:** Docker multi-stage builds (`python:3.12-slim`, `node:20-alpine`)
* **Orchestration:** Docker Compose (Local & on-premise hospital deployment)
* **CI/CD:** GitHub Actions (Automated `ruff` linting, `pytest` clinical safety suite, `flutter analyze`, and `flutter test`)

---

## 3. End-to-End Compatibility & Protocol Matrix

```
┌──────────────────────────────┬──────────────────────────────┬────────────────────────────────┐
│ Source Component             │ Target Component             │ Protocol / Latency             │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────┤
│ Flutter Kiosk                │ FastAPI Gateway              │ WebSockets (Audio) / < 50ms    │
│ FastAPI Gateway              │ Sarvam Saaras (STT)          │ Async Streaming / < 300ms      │
│ FastAPI Gateway              │ Sarvam Vision 3B VLM (OCR)   │ Multipart HTTPS / < 2.0s       │
│ FastAPI Gateway              │ Eka Care ABDM APIs           │ REST + Webhooks / < 400ms      │
│ FastAPI Gateway              │ Supabase PostgreSQL 16       │ Asyncpg Connection Pool / < 5ms│
│ Supabase Realtime (CDC)      │ Next.js Doctor Portal        │ WebSockets / < 80ms            │
│ Generated Data Contract      │ NRCeS / ABDM National Server │ HL7 FHIR R4 DocumentBundle     │
└──────────────────────────────┴──────────────────────────────┴────────────────────────────────┘
```

---

## 4. Key Packages & Dependencies Manifest

### Flutter (`pubspec.yaml` snippet)
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.5.1
  riverpod_annotation: ^2.3.5
  go_router: ^14.2.0
  dio: ^5.4.3+1
  retrofit: ^4.1.0
  hive_flutter: ^1.1.0
  flutter_secure_storage: ^9.2.2
  flutter_sound: ^9.2.13
  camera: ^0.11.0+1
  google_fonts: ^6.2.1

dev_dependencies:
  build_runner: ^2.4.9
  riverpod_generator: ^2.4.0
  retrofit_generator: ^8.1.0
  flutter_test:
    sdk: flutter
```

### Backend (`requirements.txt` snippet)
```text
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
sarvamai==0.1.4
fhir.resources==7.1.0
asyncpg==0.29.0
supabase==2.5.0
redis==5.0.6
cryptography==42.0.8
langgraph==0.0.65
pytest==8.2.2
ruff==0.4.8
```

### Doctor Portal (`package.json` snippet)
```json
{
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "^5.5.0",
    "tailwindcss": "^3.4.4",
    "@supabase/supabase-js": "^2.43.4",
    "@tanstack/react-query": "^5.45.0",
    "zustand": "^4.5.2",
    "@react-pdf/renderer": "^3.4.4",
    "lucide-react": "^0.395.0"
  }
}
```
