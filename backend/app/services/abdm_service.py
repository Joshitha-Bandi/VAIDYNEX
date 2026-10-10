import uuid
import datetime
import json
from typing import Dict, Any, Optional, List
from ..models.schemas import PatientProfile, Gender, CoverageEligibilityResponse
from ..db import supabase


class ABDMService:

    def verify_abha(self, query: str) -> PatientProfile:
        try:
            res = (
                supabase.table("patients")
                .select("*")
                .or_(
                    f"abha_number.eq.{query},phone.eq.{query},id.eq.{query}"
                )
                .limit(1)
                .execute()
            )
            if res.data:
                p = res.data[0]
                return PatientProfile(
                    patient_id=p["id"],
                    abha_number=p["abha_number"] or "",
                    abha_address=p["abha_address"] or "",
                    full_name=p["full_name"],
                    gender=Gender.MALE if p["gender"].upper() == "MALE" else Gender.FEMALE,
                    year_of_birth=datetime.datetime.now().year - p["age"],
                    address={"state": "Telangana", "district": "Khammam"},
                    pmjay_eligible=(p.get("pmjay_status") == "ACTIVE"),
                )
        except Exception as e:
            print("ABDMService.verify_abha error:", e)

        # Demo fallback
        return PatientProfile(
            patient_id="pat-048291",
            abha_number="91-4829-1029-4821",
            abha_address="ramesh.chandra@abdm",
            full_name="Ramesh Chandra",
            gender=Gender.MALE,
            year_of_birth=1974,
            address={"state": "Telangana", "district": "Khammam"},
            pmjay_eligible=True,
        )

    def create_nha_abha(
        self,
        full_name: str,
        age: int,
        gender: str,
        phone: str,
        aadhaar: Optional[str] = None,
        state: str = "Telangana",
        district: str = "Khammam",
        pincode: str = "507001",
    ) -> Dict[str, Any]:
        patient_id = f"pat-{uuid.uuid4().hex[:6]}"
        rand_num = uuid.uuid4().hex[:12]
        abha_number = f"91-{rand_num[0:4]}-{rand_num[4:8]}-{rand_num[8:12]}"
        clean_name = "".join(e for e in full_name.lower() if e.isalnum())
        abha_address = f"{clean_name}.{rand_num[:4]}@abdm"
        masked_aadhaar = (
            f"XXXX-XXXX-{aadhaar[-4:]}"
            if aadhaar and len(aadhaar) >= 4
            else f"XXXX-XXXX-{rand_num[:4]}"
        )
        pmjay_id = f"PMJAY-TS-{rand_num[:6]}"
        yob = datetime.datetime.now().year - age
        created_at = datetime.datetime.now().isoformat()

        row = {
            "id": patient_id,
            "full_name": full_name,
            "age": age,
            "gender": gender.upper(),
            "phone": phone,
            "abha_number": abha_number,
            "abha_address": abha_address,
            "aadhaar_masked": masked_aadhaar,
            "pmjay_status": "ACTIVE",
            "pmjay_id": pmjay_id,
            "auth_method": "ABDM M1 Government Registration",
        }
        try:
            supabase.table("patients").insert(row).execute()
        except Exception as e:
            print("ABDMService.create_nha_abha DB error:", e)

        return {
            "patient_id": patient_id,
            "full_name": full_name,
            "age": age,
            "year_of_birth": yob,
            "gender": gender,
            "phone": phone,
            "abha_number": abha_number,
            "abha_address": abha_address,
            "aadhaar_masked": masked_aadhaar,
            "state": state,
            "district": district,
            "pincode": pincode,
            "pmjay_status": "ACTIVE",
            "pmjay_id": pmjay_id,
            "auth_method": "ABDM M1 Government Registration",
            "kyc_status": "VERIFIED_UIDAI_NHA",
            "created_at": created_at,
        }

    def check_coverage_eligibility(self, abha_number: str) -> CoverageEligibilityResponse:
        return CoverageEligibilityResponse(
            eligible=True,
            scheme_name="PM-JAY (Pradhan Mantri Jan Arogya Yojana)",
            coverage_amount_inr=500000.0,
            beneficiary_id=f"PMJAY-BEN-{uuid.uuid4().hex[:6].upper()}",
            status="ACTIVE",
            message="Patient is eligible for cashless treatment up to ₹5,00,000 per year under PM-JAY.",
        )

    def push_approved_encounter_to_ndhm(
        self,
        encounter_id: str,
        patient_id: str,
        patient_name: str,
        abha_id: str,
        token_number: str,
        diagnosis: str,
        prescription: Any = None,
        soap: Any = None,
    ) -> Dict[str, Any]:
        tx_id = f"ABDM-TX-{uuid.uuid4().hex[:10].upper()}"
        fhir_id = f"urn:uuid:{uuid.uuid4()}"
        pmjay_claim = f"PMJAY-CLM-{uuid.uuid4().hex[:6].upper()}"
        now_str = datetime.datetime.now().isoformat()

        row = {
            "transaction_id": tx_id,
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "abha_id": abha_id,
            "token_number": token_number,
            "diagnosis": diagnosis,
            "prescription_json": prescription if prescription is not None else [],
            "soap_json": soap if soap is not None else {},
            "fhir_bundle_id": fhir_id,
            "abdm_status": "M2_CARE_CONTEXT_LINKED_GOVT_DB",
            "pmjay_claim_id": pmjay_claim,
        }
        try:
            supabase.table("abdm_transactions").insert(row).execute()
        except Exception as e:
            print("ABDMService.push_approved_encounter_to_ndhm DB error:", e)

        return {
            "status": "SUCCESS_PUSHED_TO_GOVT_DB",
            "transaction_id": tx_id,
            "encounter_id": encounter_id,
            "patient_name": patient_name,
            "abha_id": abha_id,
            "token_number": token_number,
            "fhir_bundle_id": fhir_id,
            "abdm_milestone": "M2_HIP_CARE_CONTEXT_LINKED",
            "pmjay_claim_status": "AUTO_PREAUTH_APPROVED",
            "pmjay_claim_id": pmjay_claim,
            "timestamp": now_str,
        }

    def get_all_abdm_transactions(self) -> List[Dict[str, Any]]:
        try:
            res = (
                supabase.table("abdm_transactions")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            return res.data or []
        except Exception as e:
            print("ABDMService.get_all_abdm_transactions error:", e)
            return []


abdm_service = ABDMService()
