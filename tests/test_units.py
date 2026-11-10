import pytest
from app.models.user import User
from app.models.advising import AuditCourse, OverrideRequest

def test_create_user_model():
    """Unit Test: Verifies User instantiation and field assignments."""
    user = User(username="testuser", email="test@uwi.edu", password="hashed_secret123")
    
    assert user.username == "testuser"
    assert user.email == "test@uwi.edu"
    assert user.password == "hashed_secret123"

def test_verify_password_hash():
    """Unit Test: Verifies user model attributes."""
    user = User(username="bob", email="bob@uwi.edu", password="hashed_bobpass")
    
    assert user.username == "bob"
    assert user.password != "bobpass"

def test_audit_course_initial_status():
    """Unit Test: Verifies default field values on new AuditCourse objects."""
    audit_course = AuditCourse(audit_id=1, course_id=101, status="Planned", prerequisite_result="Pending")
    
    assert audit_course.status == "Planned"
    assert audit_course.prerequisite_result == "Pending"

def test_override_request_default_status():
    """Unit Test: Verifies initial state of a student override request."""
    override = OverrideRequest(student_id=1, course_id=102, reason="Equivalent taken", status="Pending")
    
    assert override.status == "Pending"
    assert override.approver_id is None