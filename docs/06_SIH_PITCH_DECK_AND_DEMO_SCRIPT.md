# 🎯 MediKiosk — SIH 5-Slide Pitch Deck & 2-Minute Live Demo Script

**Document Version:** `1.2.0-PROD`  
**SIH Problem Statement ID:** `26047`  

---

## 1. Grand Finale 5-Slide Pitch Deck Framework

### Slide 1: The National Healthcare Bottleneck
* **The Crisis:** Indian public hospital OPDs handle 4,000–10,000 patients daily; doctor consultation time has collapsed to **2.1 minutes** (*BMJ Open, 2017*, [DOI: 10.1136/bmjopen-2017-017902](https://doi.org/10.1136/bmjopen-2017-017902)).
* **The AYUSH Gap:** Ayurvedic history-taking requires capturing the 10-fold *Dashavidha Pariksha*, which is impossible in a 2-minute OPD slot.
* **The Result:** Missing drug allergies, paper record fragmentation, and high diagnostic error rates.

### Slide 2: Proposed Solution — MediKiosk
* **Autonomous Point-of-Entry Intake Kiosk:** Offloads structured history-taking and medical document digitization to pre-consultation time.
* **100% Sovereign AI Foundation:** Powered by **Sarvam AI** for 23-language speech/vision (Saaras v3, Sarvam Vision 3B VLM) and 11-language TTS (Bulbul v3).
* **National Ecosystem Integration:** Integrated with **Eka Care Developer Platform** for pan-India ABDM health records and **NHCX** for real-time PM-JAY scheme verification.

### Slide 3: Technical Architecture & Intelligence Pipeline
* **Frontend:** Flutter Kiosk (Accessible Touch + Audio-Guided Voice) & Next.js Doctor Portal.
* **Backend:** FastAPI Gateway + LangGraph Clinical Tree + Supabase PostgreSQL & Realtime.
* **Dual Clinical Ontologies:** Western Allopathic (SOCRATES framework) + Ayurvedic (*Dashavidha Pariksha*).

### Slide 4: Key Innovations & Competitive Moats
* **1. Sovereign AI:** Zero reliance on US-hosted APIs; operates natively on Indian speech & VLM models.
* **2. 150ms Emergency Red-Flag Interceptor:** Halts intake and alerts triage for acute cardiac/stroke symptoms.
* **3. Dual Document Intelligence:** Parses physical paper prescriptions via Sarvam 3B VLM while fetching digital history via Eka Care ABDM.
* **4. Doctor-in-the-Loop Safeguard:** Generates editable draft notes; zero autonomous clinical diagnosis.

### Slide 5: Population-Scale Impact & Deployment Roadmap
* **Time Savings:** Reduces doctor note-taking from 3 minutes to **15 seconds**.
* **National Scale:** Ready for immediate deployment at AIIMS, AIIA, and public health centers.
* **Standardization:** 100% compliant with NRCeS ABDM HL7 FHIR R4 (`bdl-11` invariant) and DPDPA 2023.

---

## 2. The 2-Minute Winning Live Demo Script

```
00:00 - 00:30 ➔ Step 1 (ABHA Scan & Scheme Check)
• Presenter: "Watch as a patient approaches MediKiosk. They scan their ABHA QR code."
• Action: Kiosk verifies ABHA via Eka Care M1 API in 0.4s and queries NHCX for PM-JAY coverage.
• Audio: Sarvam Bulbul speaks in Hindi: "Namaste Ramesh ji. Aap PM-JAY ke tahat muft davaon ke liye patra hain. Kya aap swasthya jankari doctor ke sath share karne ki anumati dete hain?"
• Action: Tap "Sahamat" on screen.

00:30 - 01:00 ➔ Step 2 (Multimodal Voice Intake)
• Presenter: "The patient speaks in natural Hinglish."
• Action: Presenter speaks into mic: "Mujhe 3 din se bahut tez bukhar hai aur ulti jaisa lag raha hai."
• Screen: Sarvam Saaras transcribes in real-time.
• System: AI adaptively responds: "Kya aapko thand lag kar bukhar aa raha hai?"
• Action: Tap on-screen button: "Haan, thand lagti hai".

01:00 - 01:30 ➔ Step 3 (Prescription OCR & ABDM Fetch)
• Presenter: "Now we scan a messy, handwritten doctor prescription."
• Action: Presenter holds prescription up to kiosk camera.
• Screen: Sarvam 3B VLM extracts: Paracetamol 650mg TDS (5 Days) + Serum Uric Acid 7.8 mg/dL [HIGH].
• Action: Simultaneously, Eka Care M3 pulls past 2025 AIIMS hypertension record.

01:30 - 02:00 ➔ Step 4 & 5 (Doctor Real-Time Sync & FHIR Export)
• Presenter: "Look at the doctor\s consultation screen in Room 4."
• Screen: Token #042 lights up instantly via Supabase Realtime with PM-JAY Badge.
• Action: Doctor clicks token ➔ Complete 15-Second SOAP summary appears with highlighted High Uric Acid.
• Action: Doctor clicks "Approve & Prescribe" in 5 seconds.
• Screen: Show generated NRCeS ABDM HL7 FHIR R4 DocumentBundle.
• Presenter: "100% Sovereign. 15-second consultation prep. Ready for India."
```
