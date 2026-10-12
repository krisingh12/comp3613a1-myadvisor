"""Workflow 1 advising models.

Complete the marked student region from the ERD before wiring persistence.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class StudentProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    student_number: str
    degree_program: str
    gpa: float = 0.0
    credit_hours_completed: int = 0


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    title: str
    credits: int = 3
    level: int = 1
    prerequisite_course_id: Optional[int] = Field(default=None, foreign_key="course.id")


class DegreeRequirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    program_name: str
    course_id: int = Field(foreign_key="course.id")
    is_mandatory: bool = True


class AdvisingAudit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="studentprofile.id")
    semester: str
    status: str = "Draft"
    submitted_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditCourse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: int = Field(foreign_key="advisingaudit.id")
    course_id: int = Field(foreign_key="course.id")
    status: str = "Planned"
    prerequisite_result: Optional[str] = "Passed"


class AdvisingNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    audit_id: int = Field(foreign_key="advisingaudit.id")
    advisor_id: int = Field(foreign_key="user.id")
    note_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OverrideRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="studentprofile.id")
    course_id: int = Field(foreign_key="course.id")
    override_type: str = Field(default="Prerequisite")
    reason: str
    status: str = Field(default="Pending")
    approver_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    actor_id: int = Field(foreign_key="user.id")
    action: str
    target_type: str
    target_id: int
    details: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)