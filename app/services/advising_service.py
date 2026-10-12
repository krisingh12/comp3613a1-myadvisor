from app.repositories.advising import AdvisingRepository


class AdvisingService:
    def __init__(self, repository: AdvisingRepository):
        self.repository = repository

    def get_student_workspace(self, user_id: int):
        return self.repository.get_student_workspace(user_id)

    def save_draft(self, user_id: int, semester: str, course_ids: list[int]):
        return self.repository.save_draft(user_id, semester, course_ids)

    def submit_audit(self, user_id: int, semester: str, course_ids: list[int]):
        return self.repository.submit_audit(user_id, semester, course_ids)

    def get_advisor_queue(self, advisor_id: int):
        return self.repository.get_pending_audits()

    def add_advisor_note(self, audit_id: int, advisor_id: int, note_text: str):
        if not note_text.strip():
            raise ValueError("Advisor note cannot be empty")
        return self.repository.add_advising_note(audit_id, advisor_id, note_text)

    def decide_audit(self, audit_id: int, decision: str):
        statuses = {
            "approve": "Approved",
            "revise": "Action Required",
        }
        if decision not in statuses:
            raise ValueError("Unsupported audit decision")
        return self.repository.update_audit_status(audit_id, statuses[decision])

    def get_admin_console(self, admin_id: int):
        return self.repository.get_admin_console()

    def update_degree_requirement(
        self,
        admin_id: int,
        program_name: str,
        course_id: int,
        is_mandatory: bool,
    ):
        if not program_name.strip():
            raise ValueError("Program name cannot be empty")
        return self.repository.update_degree_requirement(
            admin_id, program_name.strip(), course_id, is_mandatory
        )

    def update_course_prerequisite(
        self,
        admin_id: int,
        course_id: int,
        prerequisite_course_id: int | None,
    ):
        return self.repository.update_course_prerequisite(
            admin_id, course_id, prerequisite_course_id
        )

    def resolve_override(self, admin_id: int, override_id: int, decision: str):
        return self.repository.resolve_override(admin_id, override_id, decision)
