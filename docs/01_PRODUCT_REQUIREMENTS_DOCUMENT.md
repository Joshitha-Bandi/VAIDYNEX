# 🏥 MediKiosk — Product Requirements Document (PRD)

**Document Version:** `1.3.0-PROD`  
**Status:** Approved for Implementation  
**SIH Problem Statement ID:** `26047`  
**Target Ministry:** Ministry of Ayush / All India Institute of Ayurveda (AIIA)  
**Primary Standards:** Ayushman Bharat Digital Mission (ABDM) | NRCeS FHIR R4 | National Health Claims Exchange (NHCX) | DPDPA 2023  
**Sovereign AI Foundation:** [Sarvam AI](https://www.sarvam.ai/) (`Saaras v3`: 23 STT Languages, `Bulbul v3`: 11 TTS Languages, `Sarvam Vision 3B VLM`: 23 Languages)  
**National Health Gateway:** [Eka Care Developer Platform](https://developer.eka.care/) (ABDM M1, M2, M3)  
**ABDM & NHCX Specifications:** [NHA Sandbox V3](https://sandbox.abdm.gov.in/) & [NRCeS FHIR R4](https://nrces.in/ndhm/fhir/r4/)  

---

## 1. Executive Summary & Sovereign Foundation

### 1.1 Vision Statement
To eliminate the severe outpatient clinical history-taking bottleneck across Indian public hospitals and AYUSH apex institutions by deploying an autonomous, accessible, multimodal clinical intake kiosk. MediKiosk converts spoken patient narration in 22 Indian languages and unstructured physical paper prescriptions into structured, physician-verified [NRCeS-compliant HL7 FHIR R4](https://nrces.in/ndhm/fhir/r4/) clinical records in under 15 seconds.

### 1.2 The Sovereign "Make in India" Technology Ecosystem
MediKiosk is engineered natively on India's Sovereign AI and Health Data infrastructure:
1. **Sarvam AI Platform:** 100% Indian-developed and sovereignly hosted speech recognition (Saaras v3 across 22 Indian languages + English), natural voice synthesis (Bulbul v3 across 11 languages with 35+ voices), and vision-language models for handwritten prescription OCR ([Sarvam AI Docs](https://www.sarvam.ai/apis/document-digitisation)).
2. **Eka Care ABDM Developer Gateway:** Certified National Health Authority (NHA) gateway integration for ABHA Milestone 1 (M1), Milestone 2 (M2 - HIP Care Context Linking), and Milestone 3 (M3 - HIU Longitudinal Records) ([Eka Developer Portal](https://developer.eka.care/user-guides/get-started)).
3. **NHCX & PM-JAY BIS Integration:** Automated coverage eligibility queries using the official **NRCeS FHIR R4 `CoverageEligibilityRequest`** profile over the National Health Claims Exchange (NHCX) and PM-JAY Beneficiary Identification System (BIS) to verify citizen entitlements in real time ([NRCeS NHCX Guidelines](https://nrces.in/ndhm/fhir/r4/)).

---

## 2. Problem Anatomy & Clinical Gap Analysis

### 2.1 The Clinical Consultation Collapse
* **Patient Density:** Apex government hospitals (AIIMS, AIIA, Safdarjung, PGI) routinely register **4,000 to 10,000 OPD patients daily**.
* **Consultation Window:** The average doctor-patient consultation time in India is **2.1 minutes** ([BMJ Open, 2017](https://doi.org/10.1136/bmjopen-2017-017902), systematic review across 67 countries).
* **Diagnostic Risk:** Classical medicine holds that 70–80% of diagnoses depend entirely on comprehensive clinical history ([Hampton et al., 1975, BMJ](https://doi.org/10.1136/bmj.2.5969.486), where 66 of 80 medical outpatients were accurately diagnosed from history alone). Under extreme 2-minute time pressure, doctors cannot simultaneously elicit history, review prior unstructured paper prescriptions, examine patients, and formulate accurate diagnoses.

### 2.2 The AYUSH Assessment Gap
Ayurvedic clinical case-taking requires capturing the 10-fold **Dashavidha Pariksha** (*Prakriti, Vikriti, Sara, Samhanana, Pramana, Satmya, Satva, Ahara Shakti, Vyayama Shakti, Vaya*) alongside *Agni* (digestive capacity) and *Koshtha* (bowel nature) ([Charaka Samhita, Vimana Sthana 8:94-130](https://www.carakasamhitaonline.com/)). Capturing this manually within a 2-minute OPD consultation is practically impossible, leading to forced abbreviation of holistic Ayurvedic care.

### 2.3 The Paper Record Fragmentation
Patients carry physical paper prescriptions, laboratory reports, and discharge summaries across multiple healthcare providers. There is no automated point-of-entry mechanism to digitize, structure, and chronologically organize these records before the patient enters the doctor's consultation room.

---

## 3. System Stakeholders & Personas

| Persona | Role | Key Needs & Pain Points |
| :--- | :--- | :--- |
| **Rural / Elderly Patient** | Primary Kiosk User | Low digital literacy, prefers regional spoken dialects (Hindi, Telugu, Tamil, Marathi), cannot navigate complex smartphone apps. |
| **OPD Physician / AYUSH Doctor** | Clinical Decision Maker | Overburdened by manual data entry; needs a 15-second structured summary with highlighted red-flag symptoms and abnormal lab values. |
| **Triage / Nursing Officer** | Emergency Responder | Needs instant, real-time alerts when high-risk emergency symptoms (cardiac, stroke, respiratory) are identified at the kiosk. |
| **Hospital Administrator / MoHFW** | Compliance & Analytics | Needs DPDPA 2023 consent compliance, ABDM M1/M2/M3 adherence, and transparent OPD throughput analytics. |

---

## 4. End-to-End 5-Step User Journey

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ STEP 1: IDENTIFY│   │ STEP 2: CONVERSE│   │  STEP 3: SCAN   │   │STEP 4: SUMMARIZE│   │ STEP 5: CONSULT │
│                 │   │                 │   │                 │   │    & ROUTE      │   │                 │
│ • Eka ABHA M1   ├──▶│ • Sarvam Saaras ├──▶│ • Sarvam 3B VLM ├──▶│ • SOAP Compiler ├──▶│ • Next.js Doctor│
│ • NHCX / PM-JAY │   │ • SOCRATES Flow │   │ • Eka M3 (Past  │   │ • Eka M2 Link   │   │   15-Sec Review │
│ • Audio Consent │   │ • Red-Flag Gate │   │   ABDM Records) │   │ • Push to HIS   │   │ • 100% Care Time│
└─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Step 1 — Identify (ABHA Auth, Scheme Eligibility & Audio Consent)
1. Patient arrives at hospital OPD point of entry.
2. Patient scans ABHA QR code or enters mobile/Aadhaar number on the Flutter Kiosk.
3. Kiosk calls **Eka Care Milestone 1 (M1)** API to verify identity and retrieve the verified 14-digit ABHA Number.
4. Kiosk queries the **NHCX / PM-JAY BIS** engine (`CoverageEligibilityRequest`) to check eligibility for PM-JAY (₹5 Lakh cashless care) or State Ayush subsidies.
5. **Sarvam Bulbul (TTS)** delivers an audio-guided consent prompt in the patient's language: *"Kya aap apne swasthya ki jaankari doctor ke sath share karne ki sahmat dete hain?"*
6. Patient taps "Sahamat / Consent Granted" $\rightarrow$ logs cryptographic consent hash under DPDPA 2023.

### Step 2 — Converse (Multimodal Voice & Touch Intake)
1. Patient speaks naturally in their dialect or Hinglish into the kiosk microphone.
2. **Sarvam Saaras v3** (supporting 22 Indian languages + English) transcribes audio via WebSockets in real time.
3. Dialogue manager navigates the clinical tree:
   * **Allopathic Branch:** SOCRATES framework (*Site, Onset, Character, Radiation, Associations, Time course, Exacerbating factors, Severity*).
   * **AYUSH Branch:** *Dashavidha Pariksha* (*Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara*).
4. **Emergency Red-Flag Interceptor:** Halts intake within 150ms if life-threatening keywords (chest pain radiating to arm, stroke signs) are detected, sounding an alarm and generating a priority triage token.

### Step 3 — Scan (Prescription Digitization & ABDM Record Pull)
1. Patient uploads physical paper prescriptions or lab reports to the kiosk high-resolution camera.
2. **Sarvam Document Digitisation 3B VLM** parses handwritten cursive text and multi-column lab tables across 23 languages.
3. Kiosk simultaneously calls **Eka Care Milestone 3 (HIU) APIs** (`/v0.5/consent-requests/init`) to fetch historical digital health records linked to the patient's ABHA account from all hospitals in India.
4. The system merges scanned paper data and historical electronic records into a unified chronological medical timeline.

### Step 4 — Summarize & Route (SOAP Generation & ABDM Linking)
1. The engine synthesizes spoken symptoms, extracted paper medications, and historical ABDM records into a structured SOAP clinical note.
2. Kiosk calls **Eka Care Milestone 2 (HIP) APIs** to bundle the encounter into an **NRCeS-compliant HL7 FHIR R4 JSON DocumentBundle** (`Composition`, `Patient`, `Encounter`, `Condition`, `MedicationStatement`, `Observation`).
3. Supabase Realtime pushes the token and structured draft summary to the designated doctor's consultation queue.

### Step 5 — Consult (15-Second Doctor Review & Clinical Approval)
1. When the patient enters the consultation room, the doctor's Next.js screen renders the **15-Second Clinical Card**.
2. Doctor reviews chief complaints, highlighted out-of-range lab tests, active medications, and PM-JAY entitlement badges in 15 seconds.
3. The doctor makes any necessary adjustments, completes physical examination, and clicks **"Approve & Prescribe"**.

---

## 5. Functional Requirements (FR)

### Module A: Conversational Multimodal History Engine
* **FR-A1 (Dual-Mode Input):** Every question must be answerable via spoken voice or on-screen touch taps.
* **FR-A2 (Indic Speech Recognition):** Integration with Sarvam Saaras v3 supporting 22 Indian languages + English (23 languages total) with code-mixed speech (Hinglish/Tanglish) handling.
* **FR-A3 (Adaptive Branching):** Dynamic questioning state machine constrained by clinical ontology (SOCRATES + Dashavidha Pariksha).
* **FR-A4 (Emergency Red-Flag Interception):** Sub-150ms detection of critical cardiac, stroke, and acute respiratory distress triggers with priority triage dispatch.

### Module B: Medical Document Digitization & Intelligence
* **FR-B1 (Multilingual Handwriting OCR):** Sarvam Vision 3B VLM ingestion of cursive doctor prescriptions and physical lab reports.
* **FR-B2 (Entity Normalization):** Extraction of medication brand names, generic names, dosages (OD, BD, TDS, HS, SOS), and durations.
* **FR-B3 (Abnormal Lab Value Highlighting):** Automated parsing of test names, observed values, units, and reference ranges with `CRITICAL_HIGH` and `CRITICAL_LOW` flags.
* **FR-B4 (ABDM Longitudinal Fetch):** Eka Care M3 HIU integration to pull prior national health records.

### Module C: Structured Clinical Summary Generator
* **FR-C1 (Standard Clinical Note Format):** Automatic compilation into Chief Complaint (CC), HPI, Past Medical/Surgical History, Drug Allergies, and Review of Systems (ROS).
* **FR-C2 (Doctor-in-the-Loop Safeguard):** The AI outputs an editable draft; zero autonomous clinical diagnosis is permitted.
* **FR-C3 (Bilingual Output):** Audio playback for patient in local language (Sarvam Bulbul in 11 languages); formatted English/Hindi clinical note for doctor.

### Module D: Consent, Privacy & ABDM Integration
* **FR-D1 (ABHA Verification):** Eka Care M1 SDK support for Aadhaar OTP, Mobile OTP, and QR Scan & Share.
* **FR-D2 (Scheme Eligibility):** NHCX FHIR R4 `CoverageEligibilityRequest` query for PM-JAY and state entitlement discovery.
* **FR-D3 (DPDPA 2023 Consent):** Cryptographically hashed, time-stamped, audio-guided consent recording.
* **FR-D4 (NRCeS HL7 FHIR R4 Bundling):** Automated generation of standard FHIR `DocumentBundle` with `Composition` root resource (`bdl-11` invariant).
* **FR-D5 (Ephemeral Session Wiping):** Complete purging of raw audio streams and temporary biometric buffers immediately upon encounter completion.

---

## 6. Non-Functional Requirements (NFR)

| Metric | Requirement Specification |
| :--- | :--- |
| **End-to-End Latency** | Speech transcription $\le 400\text{ms}$; Document OCR $\le 2.5\text{s}$; Summary Generation $\le 1.0\text{s}$. |
| **Availability & Uptime** | 99.95% availability for public hospital OPD hours (08:00 to 20:00 IST). |
| **Security & Encryption** | AES-256 GCM encryption at rest; TLS 1.3 in transit; PostgreSQL Row Level Security (RLS). |
| **Concurrency** | Scalable to 10,000 concurrent active kiosk sessions across 500 hospital locations. |
| **Acoustic Noise Resilience** | Operates reliably at $\ge 70\text{ dB}$ ambient noise typical of crowded Indian public hospital OPD waiting halls. |

---

## 7. Acceptance Criteria & Sign-Off Matrix

1. **Patient Intake Time:** A first-time, low-literacy patient completes voice intake in $\le 90\text{ seconds}$.
2. **Doctor Review Time:** Doctor reviews and approves the clinical summary in $\le 15\text{ seconds}$.
3. **Prescription Parsing Accuracy:** Character accuracy $\ge 92\%$ on handwritten cursive prescriptions.
4. **Red-Flag Recall:** 100% recall on designated acute emergency symptom vectors.
5. **ABDM Interoperability:** 100% valid HL7 FHIR R4 DocumentBundle validation against NRCeS ABDM schema specifications (`bdl-11` compliant).
