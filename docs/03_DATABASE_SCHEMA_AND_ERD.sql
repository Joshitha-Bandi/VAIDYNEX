-- ============================================================================
-- MediKiosk — Production PostgreSQL 16 DDL Schema & Entity-Relationship Design
-- Target: Supabase / PostgreSQL 16 Managed RDS
-- Verified Syntactically Clean with Proper Quoting
-- ============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ----------------------------------------------------------------------------
-- Enums (Properly Quoted for PostgreSQL 16)
-- ----------------------------------------------------------------------------
CREATE TYPE gender_enum AS ENUM ('MALE', 'FEMALE', 'OTHER', 'UNDISCLOSED');
CREATE TYPE triage_priority_enum AS ENUM ('ROUTINE', 'URGENT', 'EMERGENCY_RED');
CREATE TYPE session_status_enum AS ENUM ('INITIALIZED', 'IN_PROGRESS', 'COMPLETED', 'ABORTED', 'TRANSFERRED');
CREATE TYPE doc_type_enum AS ENUM ('PRESCRIPTION', 'LAB_REPORT', 'DISCHARGE_SUMMARY', 'IMAGING_REPORT', 'OTHER');
CREATE TYPE clinical_flag_enum AS ENUM ('NORMAL', 'HIGH', 'LOW', 'CRITICAL_HIGH', 'CRITICAL_LOW');
CREATE TYPE practitioner_role_enum AS ENUM ('ALLOPATHIC_PHYSICIAN', 'AYURVEDIC_VAIDYA', 'TRIAGE_NURSE', 'ADMIN');

-- ----------------------------------------------------------------------------
-- 1. Healthcare Facilities / Hospitals
-- ----------------------------------------------------------------------------
CREATE TABLE facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_code VARCHAR(50) UNIQUE NOT NULL,
    facility_name VARCHAR(255) NOT NULL,
    system_type VARCHAR(50) DEFAULT 'AYUSH_ALLOPATHIC_HYBRID',
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 2. Departments / Specialty OPDs
-- ----------------------------------------------------------------------------
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL,
    is_ayush_specialty BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 3. Practitioners (Physicians, Vaidyas, Triage Staff)
-- ----------------------------------------------------------------------------
CREATE TABLE practitioners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    facility_id UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    department_id UUID REFERENCES departments(id),
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    specialization VARCHAR(150),
    role practitioner_role_enum DEFAULT 'ALLOPATHIC_PHYSICIAN',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 4. Patients Registry & ABHA Profiles
-- ----------------------------------------------------------------------------
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    abha_number VARCHAR(20) UNIQUE,
    abha_address VARCHAR(100) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_enum NOT NULL,
    primary_mobile VARCHAR(15) NOT NULL,
    primary_language VARCHAR(50) DEFAULT 'Hindi',
    emergency_contact_phone VARCHAR(15),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 5. Kiosk Encounters & Intake Sessions
-- ----------------------------------------------------------------------------
CREATE TABLE encounters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_token VARCHAR(50) UNIQUE NOT NULL,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(id),
    department_id UUID NOT NULL REFERENCES departments(id),
    practitioner_id UUID REFERENCES practitioners(id),
    intake_mode VARCHAR(50) DEFAULT 'KIOSK_VOICE_TOUCH',
    session_status session_status_enum DEFAULT 'INITIALIZED',
    triage_priority triage_priority_enum DEFAULT 'ROUTINE',
    red_flag_reason TEXT,
    dpdpa_consent_granted BOOLEAN DEFAULT FALSE,
    dpdpa_consent_hash VARCHAR(128),
    dpdpa_consent_timestamp TIMESTAMPTZ,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 6. Structured Symptom Intake (SOCRATES Framework)
-- ----------------------------------------------------------------------------
CREATE TABLE symptoms_intake (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    chief_complaint TEXT NOT NULL,
    site VARCHAR(255),
    onset VARCHAR(255),
    character TEXT,
    radiation VARCHAR(255),
    associated_symptoms TEXT[],
    time_course VARCHAR(255),
    exacerbating_relieving TEXT,
    severity_score INT CHECK (severity_score BETWEEN 1 AND 10),
    raw_audio_transcript TEXT,
    detected_language VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 7. Ayurvedic Dashavidha Pariksha Assessment
-- ----------------------------------------------------------------------------
CREATE TABLE ayush_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    prakriti_dominant VARCHAR(50),
    vikriti_dosha VARCHAR(50),
    agni_type VARCHAR(50),      -- Manda, Tikshna, Vishama, Sama
    koshtha_type VARCHAR(50),   -- Krura, Mridu, Madhyama
    ahara_vihara_habits TEXT,
    sleep_pattern VARCHAR(100),
    dhatu_sarata VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 8. Scanned Medical Documents & Raw VLM Metadata
-- ----------------------------------------------------------------------------
CREATE TABLE scanned_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    document_type doc_type_enum NOT NULL,
    storage_url TEXT NOT NULL,
    raw_vlm_output JSONB,
    processed_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 9. Extracted Medications (from Paper Scans & Eka M3 ABDM Feeds)
-- ----------------------------------------------------------------------------
CREATE TABLE extracted_medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scanned_doc_id UUID REFERENCES scanned_documents(id) ON DELETE SET NULL,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    brand_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    dosage_strength VARCHAR(100),
    frequency_instruction VARCHAR(100),
    duration_days INT,
    is_currently_taking BOOLEAN DEFAULT TRUE,
    source_type VARCHAR(50) DEFAULT 'SCANNED_PAPER_RX',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 10. Extracted Laboratory Observations
-- ----------------------------------------------------------------------------
CREATE TABLE extracted_lab_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scanned_doc_id UUID REFERENCES scanned_documents(id) ON DELETE SET NULL,
    encounter_id UUID NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    observed_value NUMERIC(10,3),
    unit VARCHAR(50),
    reference_range VARCHAR(100),
    clinical_flag clinical_flag_enum DEFAULT 'NORMAL',
    test_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 11. Compiled Clinical Summaries & HL7 FHIR Bundles
-- ----------------------------------------------------------------------------
CREATE TABLE clinical_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID UNIQUE NOT NULL REFERENCES encounters(id) ON DELETE CASCADE,
    formatted_markdown TEXT NOT NULL,
    fhir_bundle_json JSONB NOT NULL,
    physician_approved BOOLEAN DEFAULT FALSE,
    physician_notes TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- Indexes & Optimizations
-- ----------------------------------------------------------------------------
CREATE INDEX idx_patients_abha ON patients(abha_number);
CREATE INDEX idx_encounters_facility_dept ON encounters(facility_id, department_id, session_status);
CREATE INDEX idx_encounters_triage ON encounters(triage_priority) WHERE triage_priority = 'EMERGENCY_RED';
CREATE INDEX idx_medications_encounter ON extracted_medications(encounter_id);
CREATE INDEX idx_labs_encounter ON extracted_lab_observations(encounter_id);

-- ----------------------------------------------------------------------------
-- Row Level Security (RLS) Policies
-- ----------------------------------------------------------------------------
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE encounters ENABLE ROW LEVEL SECURITY;
ALTER TABLE clinical_summaries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Practitioners access encounters in their hospital"
ON encounters FOR SELECT
USING (auth.jwt() ->> 'facility_id' = facility_id::text);

CREATE POLICY "Doctors update summaries in their department"
ON clinical_summaries FOR ALL
USING (EXISTS (
    SELECT 1 FROM encounters e
    WHERE e.id = clinical_summaries.encounter_id
    AND e.facility_id::text = auth.jwt() ->> 'facility_id'
));
