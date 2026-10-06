from fastapi.testclient import TestClient
from app import app, db

client = TestClient(app)

def test_initiate_reference_check():
    """Verifies that the automated outreach loop initializes cleanly and spins out tracking tokens."""
    response = client.post(
        "/v1/screening/request?candidate_name=JaneDoe&candidate_ip=192.168.1.50&referee_email=manager@corp.com"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert "token" in response.json()

def test_fraud_detection_trigger():
    """Validates that identical digital fingerprints trigger automated compliance alerts."""
    # Step 1: Create request
    init_res = client.post(
        "/v1/screening/request?candidate_name=JohnDoe&candidate_ip=127.0.0.1&referee_email=friend@web.com"
    )
    token = init_res.json()["token"]
    
    # Step 2: Submit from the same IP (127.0.0.1) to trigger fraud validation rules
    payload = {"scores": {"reliability": 5}, "comments": "Excellent worker"}
    sub_res = client.post(f"/v1/screening/submit?token={token}", json=payload)
    
    assert sub_res.status_code == 200
    assert sub_res.json()["fraud_alert_triggered"] is True
    assert len(db["fraud_logs"]) > 0
