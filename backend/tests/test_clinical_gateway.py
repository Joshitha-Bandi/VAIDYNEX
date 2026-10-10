from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

def test_abha_verification():
    res = client.post("/api/v1/abdm/abha/verify", json={"abha_number": "91-4829-1029-4821"})
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Ramesh Chandra"
    assert data["gender"] == "MALE"

def test_insurance_eligibility():
    res = client.post("/api/v1/insurance/coverage-eligibility/check", json={"patient_id": "pat-048291", "abha_number": "91-4829-1029-4821"})
    assert res.status_code == 200
    data = res.json()
    assert data["eligible"] is True
    assert "PM-JAY" in data["scheme_name"]

def test_red_flag_interceptor():
    res = client.post("/api/v1/intake/chat", json={
        "encounter_id": "enc-0042",
        "patient_id": "pat-048291",
        "current_input": "Mujhe chest pain aur left arm pain ho raha hai",
        "messages": []
    })
    assert res.status_code == 200
    data = res.json()
    assert data["red_flag"]["is_triggered"] is True
    assert data["red_flag"]["latency_ms"] < 150

def test_document_ocr_extraction():
    res = client.post("/api/v1/documents/ocr", json={"encounter_id": "enc-0042"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["medications"]) > 0
    assert len(data["lab_results"]) > 0
    assert any(lab["test_name"] == "Serum Uric Acid" and lab["is_abnormal"] for lab in data["lab_results"])

def test_doctor_queue_and_soap():
    res = client.get("/api/v1/doctor/queue")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    
    res_soap = client.get("/api/v1/doctor/encounter/enc-0042/soap")
    assert res_soap.status_code == 200
    assert "Osteoarthritis" in res_soap.json()["assessment"]

def test_nrces_fhir_bundle():
    res = client.get("/api/v1/doctor/encounter/enc-0042/fhir")
    assert res.status_code == 200
    bundle = res.json()
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "document"
    assert bundle["entry"][0]["resource"]["resourceType"] == "Composition"
