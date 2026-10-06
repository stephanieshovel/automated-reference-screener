import os
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks

app = FastAPI(title="Automated Talent Acquisition Reference Screener")

# Mock Database
db = {
    "candidates": {},
    "references": {},
    "fraud_logs": []
}

def send_mock_email(email_type: str, email: str, link: str):
    """Simulates an optimized outbound enterprise email worker loop."""
    print(f"[EMAIL WORKER] [{datetime.utcnow()}] Sending {email_type} to {email} with link: {link}")

@app.post("/v1/screening/request")
async def initiate_reference_check(candidate_name: str, candidate_ip: str, referee_email: str, background_tasks: BackgroundTasks):
    """
    Step 1: Triggers the automated screening loop.
    Generates a secure, tokenized invitation link for the referee.
    """
    token = str(uuid.uuid4())
    expiration = datetime.utcnow() + timedelta(days=7)
    
    # Store reference request metadata
    db["references"][token] = {
        "candidate_name": candidate_name,
        "candidate_ip": candidate_ip,
        "referee_email": referee_email,
        "status": "Pending Outreach",
        "expires_at": expiration
    }
    
    secure_link = f"https://ta-screener.io{token}"
    
    # Offload email generation to a background task for sub-millisecond API response
    background_tasks.add_task(send_mock_email, "Reference Request", referee_email, secure_link)
    db["references"][token]["status"] = "Awaiting Response"
    
    return {"status": "Success", "message": "Outreach pipeline initialized.", "token": token}

@app.post("/v1/screening/submit")
async def submit_screening_survey(token: str, request: Request, scores: dict, comments: str):
    """
    Step 2 & 3: Captures feedback data and runs automated fraud cross-checks.
    Isolates shared digital fingerprints between candidate and referee.
    """
    if token not in db["references"]:
        raise HTTPException(status_code=404, detail="Invalid or expired screening token.")
        
    ref_data = db["references"][token]
    
    if datetime.utcnow() > ref_data["expires_at"]:
        ref_data["status"] = "Expired"
        raise HTTPException(status_code=400, detail="Screening window has expired.")

    # Automated IP Fingerprint Fraud Cross-Check
    client_ip = request.client.host
    fraud_detected = False
    if client_ip == ref_data["candidate_ip"]:
        fraud_detected = True
        fraud_entry = {
            "candidate": ref_data["candidate_name"],
            "referee": ref_data["referee_email"],
            "flag": "IP Match / Self-Reference Suspicion",
            "timestamp": datetime.utcnow()
        }
        db["fraud_logs"].append(fraud_entry)

    # Persist the processed screening evaluation data
    db["candidates"][ref_data["candidate_name"]] = {
        "referee": ref_data["referee_email"],
        "scores": scores,
        "comments": comments,
        "fraud_flagged": fraud_detected,
        "completed_at": datetime.utcnow()
    }
    
    ref_data["status"] = "Completed"
    
    return {
        "status": "Processed", 
        "fraud_alert_triggered": fraud_detected,
        "message": "Reference screening compiled cleanly."
    }
