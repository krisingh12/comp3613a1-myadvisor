from datetime import datetime

from sqlmodel import Session, select

from app.models.advising import (
    AdvisingAudit,
    AuditCourse,
    Course,
    DegreeRequirement,
    StudentProfile,
    AdvisingNote,
    AuditLog,
    OverrideRequest,
)
from app.models.user import User


class AdvisingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_student_workspace(self, user_id: int):
        profile = self.db.exec(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        ).one_or_none()
        if profile is None:
            return {
                "profile": None,
                "audit": None,
                "requirements": [],
                "courses": [],
                "selected_course_ids": [],
            }

        audit = self.db.exec(
            select(AdvisingAudit)
            .where(AdvisingAudit.student_id == profile.id)
            .order_by(AdvisingAudit.updated_at.desc())
        ).first()
        requirements = self.db.exec(
            select(DegreeRequirement)
            .where(DegreeRequirement.program_name == profile.degree_program)
        ).all()
        courses = self.db.exec(select(Course)).all()
        selected_course_ids = []
        prerequisite_results = {}
        if audit is not None:
            audit_courses = self.db.exec(
                select(AuditCourse).where(AuditCourse.audit_id == audit.id)
            ).all()
            selected_course_ids = [item.course_id for item in audit_courses]
            prerequisite_results = {
                item.course_id: item.prerequisite_result for item in audit_courses
            }

        return {
            "profile": profile,
            "audit": audit,
            "requirements": requirements,
            "courses": courses,
            "selected_course_ids": selected_course_ids,
            "prerequisite_results": prerequisite_results,
        }

    def save_draft(self, user_id: int, semester: str, course_ids: list[int]):
        profile = self.db.exec(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        ).one_or_none()
        if profile is None:
            raise ValueError("Student profile is required before planning an audit")

        audit = self.db.exec(
            select(AdvisingAudit)
            .where(
                AdvisingAudit.student_id == profile.id,
                AdvisingAudit.status == "Draft",
            )
            .order_by(AdvisingAudit.updated_at.desc())
        ).first()
        if audit is None:
            audit = AdvisingAudit(
                student_id=profile.id,
                semester=semester,
                status="Draft",
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(audit)

        self.db.query(AuditCourse).filter(AuditCourse.audit_id == audit.id).delete()
        for course_id in course_ids:
            self.db.add(
                AuditCourse(
                    audit_id=audit.id,
                    course_id=course_id,
                    status="Planned",
                    prerequisite_result="Pending",
                )
            )
        audit.updated_at = datetime.utcnow()
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def submit_audit(self, user_id: int, semester: str, course_ids: list[int]):
        audit = self.save_draft(user_id, semester, course_ids)
        audit.status = "Pending Approval"
        audit.submitted_at = datetime.utcnow()
        audit.updated_at = audit.submitted_at
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def get_pending_audits(self):
        audits = self.db.exec(
            select(AdvisingAudit)
            .where(AdvisingAudit.status == "Pending Approval")
            .order_by(AdvisingAudit.submitted_at.asc())
        ).all()
        queue = []
        for audit in audits:
            profile = self.db.get(StudentProfile, audit.student_id)
            student = self.db.get(User, profile.user_id) if profile else None
            audit_courses = self.db.exec(
                select(AuditCourse).where(AuditCourse.audit_id == audit.id)
            ).all()
            courses = [
                {
                    "course": self.db.get(Course, item.course_id),
                    "status": item.status,
                    "prerequisite_result": item.prerequisite_result,
                }
                for item in audit_courses
            ]
            notes = self.db.exec(
                select(AdvisingNote)
                .where(AdvisingNote.audit_id == audit.id)
                .order_by(AdvisingNote.created_at.desc())
            ).all()
            queue.append(
                {
                    "audit": audit,
                    "profile": profile,
                    "student": student,
                    "courses": courses,
                    "notes": notes,
                }
            )
        return queue

    def add_advising_note(self, audit_id: int, advisor_id: int, note_text: str):
        note = AdvisingNote(
            audit_id=audit_id,
            advisor_id=advisor_id,
            note_text=note_text.strip(),
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def update_audit_status(self, audit_id: int, status: str):
        audit = self.db.get(AdvisingAudit, audit_id)
        if audit is None:
            raise ValueError("Audit does not exist")
        audit.status = status
        audit.updated_at = datetime.utcnow()
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def get_admin_console(self):
        return {
            "courses": self.db.exec(select(Course).order_by(Course.code)).all(),
            "requirements": self.db.exec(
                select(DegreeRequirement).order_by(
                    DegreeRequirement.program_name,
                    DegreeRequirement.course_id,
                )
            ).all(),
            "overrides": self.db.exec(
                select(OverrideRequest)
                .where(OverrideRequest.status == "Pending")
                .order_by(OverrideRequest.created_at.asc())
            ).all(),
            "logs": self.db.exec(
                select(AuditLog).order_by(AuditLog.created_at.desc()).limit(20)
            ).all(),
        }

    def _record_admin_log(
        self,
        actor_id: int,
        action: str,
        target_type: str,
        target_id: int,
        details: str,
    ):
        self.db.add(
            AuditLog(
                actor_id=actor_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                details=details,
            )
        )

    def update_degree_requirement(
        self,
        actor_id: int,
        program_name: str,
        course_id: int,
        is_mandatory: bool,
    ):
        requirement = self.db.exec(
            select(DegreeRequirement).where(
                DegreeRequirement.program_name == program_name,
                DegreeRequirement.course_id == course_id,
            )
        ).one_or_none()
        if requirement is None:
            requirement = DegreeRequirement(
                program_name=program_name,
                course_id=course_id,
                is_mandatory=is_mandatory,
            )
        else:
            requirement.is_mandatory = is_mandatory
        self.db.add(requirement)
        self.db.commit()
        self.db.refresh(requirement)
        self._record_admin_log(
            actor_id,
            "Update degree requirement",
            "DegreeRequirement",
            requirement.id,
            f"{program_name} / course {course_id}; mandatory={is_mandatory}",
        )
        self.db.commit()
        return requirement

    def update_course_prerequisite(
        self,
        actor_id: int,
        course_id: int,
        prerequisite_course_id: int | None,
    ):
        course = self.db.get(Course, course_id)
        if course is None:
            raise ValueError("Course does not exist")
        if prerequisite_course_id == course_id:
            raise ValueError("A course cannot be its own prerequisite")
        course.prerequisite_course_id = prerequisite_course_id
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        self._record_admin_log(
            actor_id,
            "Update prerequisite rule",
            "Course",
            course.id,
            f"prerequisite_course_id={prerequisite_course_id}",
        )
        self.db.commit()
        return course

    def resolve_override(
        self,
        actor_id: int,
        override_id: int,
        decision: str,
    ):
        if decision not in {"Approved", "Rejected"}:
            raise ValueError("Unsupported override decision")
        override = self.db.get(OverrideRequest, override_id)
        if override is None:
            raise ValueError("Override request does not exist")
        override.status = decision
        override.approver_id = actor_id
        self.db.add(override)
        self.db.commit()
        self.db.refresh(override)
        self._record_admin_log(
            actor_id,
            f"{decision} override request",
            "OverrideRequest",
            override.id,
            override.reason,
        )
        self.db.commit()
        return override
