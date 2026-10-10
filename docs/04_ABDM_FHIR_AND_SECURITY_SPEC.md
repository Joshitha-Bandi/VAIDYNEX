# 🔐 MediKiosk — ABDM Architecture, NRCeS FHIR R4, M3_V1, NHCX & DPDPA 2023 Specification

**Document Version:** `1.3.0-PROD`  
**Status:** Approved for Implementation  
**NHA Standards:** [NRCeS FHIR R4 Profiles](https://nrces.in/ndhm/fhir/r4/) | [ABDM_M3_V1 HIU Specification](https://sandbox.abdm.gov.in/sandbox/v3/new-documentation?doc=ABDM_M3_V1) | [National Health Claims Exchange (NHCX)](https://nrces.in/ndhm/fhir/r4/)  
**SIH Problem Statement ID:** `26047`  

---

## 1. ABDM & NHCX National Digital Health Architecture

The National Health Authority (NHA) digital health infrastructure integrates patient identity, clinical data exchange, and insurance scheme eligibility across 5 standardized layers:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 NHA DIGITAL HEALTH ECOSYSTEM LAYERS                              │
├──────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│ 1. Identity Layer (ABDM M1)              │ ABHA Number (14-Digit) + ABHA Address (name@abdm)     │
│ 2. Registry Layer (HFR / HPR)            │ Health Facility Registry (HFR) + Healthcare Pro (HPR) │
│ 3. Coverage Eligibility (NHCX / BIS)     │ CoverageEligibilityRequest (PM-JAY & State Schemes)   │
│ 4. Data Exchange (ABDM M2/M3)            │ NRCeS FHIR R4 DocumentBundle via Curve25519 + AES-GCM │
│ 5. Unified Health Interface (UHI)        │ Open Network Protocol for Teleconsultation & Booking  │
└──────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 2. NHCX Scheme & Insurance Eligibility Verification (`CoverageEligibilityRequest`)

### 2.1 Clinical & Social Objective
In public hospitals, patients frequently pay out-of-pocket for diagnostic tests and medicines because they are unaware of their active entitlement under **Ayushman Bharat PM-JAY (₹5 Lakh annual coverage)** or state-sponsored health programs.

When a patient identifies themselves at MediKiosk via ABHA, the kiosk queries the **National Health Claims Exchange (NHCX)** using the official **NRCeS FHIR R4 `CoverageEligibilityRequest`** profile:

```mermaid
sequenceDiagram
    autonumber
    participant Patient as Patient at MediKiosk
    participant Kiosk as Flutter MediKiosk UI
    participant Gateway as FastAPI Gateway
    participant NHCX as NHA NHCX / PM-JAY BIS Gateway
    participant Doctor as Doctor Next.js Portal

    Patient->>Kiosk: Scans ABHA QR / Enters Mobile Number
    Kiosk->>Gateway: POST /api/v1/insurance/coverage-eligibility/check
    Gateway->>NHCX: POST /v1/CoverageEligibilityRequest (FHIR R4 Bundle)
    NHCX-->>Gateway: Returns CoverageEligibilityResponse (PM-JAY Active: ₹5 Lakh)
    Gateway-->>Kiosk: Benefit Status: "Eligible for Free AYUSH OPD & Medicines (PM-JAY)"
    Kiosk->>Patient: Sarvam Bulbul Voice: "Aap Ayushman Bharat PM-JAY ke tahat muft dawaon ke liye patra hain."
    Gateway->>Doctor: Flags "PM-JAY Beneficiary (Cashless Care)" Badge on Doctor Dashboard
```

---

### 2.2 NRCeS FHIR R4 `CoverageEligibilityRequest` Payload Contract

```json
{
  "resourceType": "CoverageEligibilityRequest",
  "id": "eligibility-req-0042",
  "meta": {
    "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/CoverageEligibilityRequest"]
  },
  "status": "active",
  "purpose": ["benefits", "discovery"],
  "patient": {
    "reference": "Patient/pat-048291",
    "identifier": {
      "system": "https://healthid.ndhm.gov.in",
      "value": "91-4829-1029-4821"
    }
  },
  "created": "2026-08-23T18:35:00Z",
  "provider": {
    "reference": "Organization/IN0110000142",
    "display": "All India Institute of Ayurveda (AIIA)"
  },
  "insurance": [
    {
      "focal": true,
      "coverage": {
        "display": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY)"
      }
    }
  ]
}
```

---

## 3. Official ABDM M3_V1 Consent & Health Data Flow (HIU Role)

```mermaid
sequenceDiagram
    autonumber
    participant Kiosk as MediKiosk (HIU Engine)
    participant NHA as NHA ABDM Gateway / Consent Manager
    participant PHR as Patient ABHA App (PHR)
    participant HIP as Remote Hospital / Lab (HIP)

    Note over Kiosk,NHA: 1. INITIATE CONSENT REQUEST
    Kiosk->>NHA: POST /v0.5/consent-requests/init (Purpose: CARETREAT, HI Types: Rx, Labs)
    NHA-->>Kiosk: POST /v0.5/consent-requests/on-init (Returns consentRequestId)

    Note over NHA,PHR: 2. PATIENT CONSENT GRANT
    NHA->>PHR: Push Notification: MediKiosk requests 1-day access for OPD Consultation
    PHR->>NHA: Patient Approves via Audio/PIN (Status: GRANTED)

    Note over NHA,Kiosk: 3. CONSENT ARTEFACT DELIVERY
    NHA->>Kiosk: POST /v0.5/consents/hiu/notify (Delivers signed consentArtefacts[])
    Kiosk->>NHA: POST /v0.5/consents/hiu/on-notify (Acknowledgment)
    Kiosk->>NHA: POST /v0.5/consents/fetch (Fetches full cryptographic artifact)
    NHA-->>Kiosk: POST /v0.5/consents/on-fetch (Cryptographic signature & permissions)

    Note over Kiosk,HIP: 4. ENCRYPTED DATA FLOW (ECDH + AES-GCM)
    Kiosk->>NHA: POST /v0.5/health-information/hiu/request (Sends HIU Public Key + Nonce)
    NHA->>HIP: POST /v0.5/health-information/hip/request
    HIP->>HIP: Encrypt FHIR Bundle with Shared ECDH Secret + AES-GCM-256
    HIP->>Kiosk: POST /v0.5/health-information/transfer (Encrypted FHIR payload)
    Kiosk->>Kiosk: Decrypt payload using Private Key ➔ Ingest into Clinical Timeline
```

---

## 4. Validated NRCeS-Compliant HL7 FHIR R4 DocumentBundle Specification

In strict compliance with **NRCeS India FHIR R4 Profile (`bdl-11` invariant)**, the root bundle is of type `document`, and **`entry[0]` is mandatory `Composition`**:

```json
{
  "resourceType": "Bundle",
  "id": "bundle-enc-0042",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2026-08-23T18:00:00Z",
    "profile": [
      "https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"
    ]
  },
  "identifier": {
    "system": "https://medikiosk.gov.in/bundles",
    "value": "MEDIKIOSK-2026-ENC-0042"
  },
  "type": "document",
  "timestamp": "2026-08-23T18:00:00Z",
  "entry": [
    {
      "fullUrl": "urn:uuid:comp-0042",
      "resource": {
        "resourceType": "Composition",
        "id": "comp-0042",
        "meta": {
          "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/OPConsultRecord"]
        },
        "status": "final",
        "type": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "371530004",
              "display": "Clinical consultation report"
            }
          ],
          "text": "Outpatient Clinical Consultation Record"
        },
        "subject": { "reference": "urn:uuid:pat-048291" },
        "encounter": { "reference": "urn:uuid:enc-0042" },
        "date": "2026-08-23T18:00:00Z",
        "author": [{ "reference": "urn:uuid:prac-01", "display": "Dr. Suresh Sharma" }],
        "title": "MediKiosk Structured Outpatient Intake Summary",
        "section": [
          {
            "title": "Chief Complaints & HPI",
            "code": { "coding": [{ "system": "http://snomed.info/sct", "code": "422843007", "display": "Chief complaint" }] },
            "entry": [{ "reference": "urn:uuid:cond-01" }]
          },
          {
            "title": "Current Medications",
            "code": { "coding": [{ "system": "http://snomed.info/sct", "code": "722442002", "display": "Medication section" }] },
            "entry": [{ "reference": "urn:uuid:med-01" }]
          },
          {
            "title": "Diagnostic Observations",
            "code": { "coding": [{ "system": "http://snomed.info/sct", "code": "423100009", "display": "Results section" }] },
            "entry": [{ "reference": "urn:uuid:obs-01" }]
          }
        ]
      }
    },
    {
      "fullUrl": "urn:uuid:pat-048291",
      "resource": {
        "resourceType": "Patient",
        "id": "pat-048291",
        "meta": {
          "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"]
        },
        "identifier": [
          {
            "system": "https://healthid.ndhm.gov.in",
            "value": "91-4829-1029-4821"
          }
        ],
        "name": [{ "text": "Ramesh Chandra", "family": "Chandra", "given": ["Ramesh"] }],
        "telecom": [{ "system": "phone", "value": "+919876543210" }],
        "gender": "male",
        "birthDate": "1974-05-12"
      }
    },
    {
      "fullUrl": "urn:uuid:enc-0042",
      "resource": {
        "resourceType": "Encounter",
        "id": "enc-0042",
        "meta": {
          "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Encounter"]
        },
        "status": "in-progress",
        "class": {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
          "code": "AMB",
          "display": "Ambulatory Outpatient"
        },
        "subject": { "reference": "urn:uuid:pat-048291" },
        "period": { "start": "2026-08-23T17:55:00Z" }
      }
    },
    {
      "fullUrl": "urn:uuid:cond-01",
      "resource": {
        "resourceType": "Condition",
        "id": "cond-01",
        "meta": {
          "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Condition"]
        },
        "clinicalStatus": {
          "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active" }]
        },
        "code": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "239873007",
              "display": "Osteoarthritis of knee (Sandhigata Vata)"
            }
          ],
          "text": "Bilateral knee joint pain with crepitus for 6 months"
        },
        "subject": { "reference": "urn:uuid:pat-048291" }
      }
    },
    {
      "fullUrl": "urn:uuid:med-01",
      "resource": {
        "resourceType": "MedicationStatement",
        "id": "med-01",
        "meta": {
          "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/MedicationStatement"]
        },
        "status": "active",
        "medicationCodeableConcept": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "318851002",
              "display": "Telmisartan 40mg Tablet"
            }
          ],
          "text": "Telma 40 (Telmisartan 40mg)"
        },
        "subject": { "reference": "urn:uuid:pat-048291" },
        "dosage": [{ "text": "1-0-0 After food daily" }]
      }
    },
    {
      "fullUrl": "urn:uuid:obs-01",
      "resource": {
        "resourceType": "Observation",
        "id": "obs-01",
        "meta": {
          "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Observation"]
        },
        "status": "final",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "3084-1",
              "display": "Urate [Mass/volume] in Serum or Plasma"
            }
          ]
        },
        "subject": { "reference": "urn:uuid:pat-048291" },
        "valueQuantity": {
          "value": 7.8,
          "unit": "mg/dL",
          "system": "http://unitsofmeasure.org",
          "code": "mg/dL"
        },
        "interpretation": [
          {
            "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", "code": "H", "display": "High" }]
          }
        ],
        "referenceRange": [{ "low": { "value": 3.5 }, "high": { "value": 7.2 } }]
      }
    }
  ]
}
```
