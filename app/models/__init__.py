"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.advising import (
    AdvisingAudit,
    AdvisingNote,
    AuditLog,
    AuditCourse,
    Course,
    DegreeRequirement,
    StudentProfile,
    OverrideRequest,
)

__all__ = [
    "User",
    "StudentProfile",
    "Course",
    "DegreeRequirement",
    "AdvisingAudit",
    "AdvisingNote",
    "OverrideRequest",
    "AuditLog",
    "AuditCourse",
]
