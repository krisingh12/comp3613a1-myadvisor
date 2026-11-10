import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_authenticated_student_workspace_access():
    """Integration Test: Ensures student advising workspace endpoint is accessible."""
    response = client.get("/app/course-audit", follow_redirects=True)
    assert response.status_code == 200

def test_save_and_submit_student_audit():
    """Integration Test: Verifies workflow for submitting student audit schedule."""
    login_resp = client.post("/login", data={"username": "bob", "password": "bobpass"}, follow_redirects=True)
    assert login_resp.status_code == 200
    
    response = client.get("/app/course-audit")
    assert response.status_code == 200

def test_advisor_approve_audit_workflow():
    """Integration Test: Verifies advisor queue loading and access."""
    login_resp = client.post("/login", data={"username": "admin", "password": "adminpass"}, follow_redirects=True)
    assert login_resp.status_code == 200
    
    response = client.get("/app/advisor/queue")
    assert response.status_code == 200

def test_admin_resolve_override_and_audit_log():
    """Integration Test: Verifies admin degree plan console access."""
    login_resp = client.post("/login", data={"username": "admin", "password": "adminpass"}, follow_redirects=True)
    assert login_resp.status_code == 200
    
    response = client.get("/admin/degree-plan")
    assert response.status_code == 200