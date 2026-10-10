from typing import Dict, Any

class NRCeSFHIRService:
    def generate_document_bundle(self, encounter_id: str, patient_id: str, soap_note: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "resourceType": "Bundle",
            "id": f"bundle-{encounter_id}",
            "meta": {
                "versionId": "1",
                "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"]
            },
            "type": "document",
            "entry": [
                {
                    "fullUrl": f"urn:uuid:comp-{encounter_id}",
                    "resource": {
                        "resourceType": "Composition",
                        "id": f"comp-{encounter_id}",
                        "status": "final",
                        "type": {
                            "coding": [{"system": "http://snomed.info/sct", "code": "371530004", "display": "Clinical consultation report"}]
                        },
                        "subject": {"reference": f"Patient/{patient_id}"},
                        "title": "MediKiosk Structured Outpatient Intake Summary",
                        "section": [
                            {"title": "Chief Complaints & HPI", "text": {"status": "generated", "div": soap_note.get("subjective", "")}},
                            {"title": "Observations & Results", "text": {"status": "generated", "div": soap_note.get("objective", "")}},
                            {"title": "Clinical Assessment", "text": {"status": "generated", "div": soap_note.get("assessment", "")}}
                        ]
                    }
                },
                {
                    "fullUrl": f"urn:uuid:pat-{patient_id}",
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient_id,
                        "name": [{"text": soap_note.get("patient_name", patient_id)}]
                    }
                }
            ]
        }

fhir_service = NRCeSFHIRService()
