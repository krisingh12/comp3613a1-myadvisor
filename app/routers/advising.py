from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.repositories.advising import AdvisingRepository
from app.services.advising_service import AdvisingService

from . import router, templates


@router.get("/app/course-audit", response_class=HTMLResponse)
async def course_audit_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    repository = AdvisingRepository(db)
    service = AdvisingService(repository)
    workspace = service.get_student_workspace(user_id=user.id)
    return templates.TemplateResponse(
        request=request,
        name="course-audit.html",
        context={"user": user, "workspace": workspace},
    )


@router.get("/app/advisor/queue", response_class=HTMLResponse)
async def advisor_queue_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    repository = AdvisingRepository(db)
    service = AdvisingService(repository)
    queue = service.get_advisor_queue(advisor_id=user.id)
    return templates.TemplateResponse(
        request=request,
        name="advisor-queue.html",
        context={"user": user, "queue": queue},
    )


@router.get("/admin/degree-plan", response_class=HTMLResponse)
async def admin_degree_plan_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    repository = AdvisingRepository(db)
    service = AdvisingService(repository)
    console = service.get_admin_console(admin_id=user.id)
    return templates.TemplateResponse(
        request=request,
        name="admin-degree-plan.html",
        context={"user": user, "console": console},
    )


@router.post("/admin/degree-plan/requirement")
def update_degree_requirement(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    program_name: str = Form(...),
    course_id: int = Form(...),
    is_mandatory: bool = Form(default=False),
):
    service = AdvisingService(AdvisingRepository(db))
    service.update_degree_requirement(
        user.id, program_name, course_id, is_mandatory
    )
    return RedirectResponse(
        url=request.url_for("admin_degree_plan_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/admin/degree-plan/prerequisite")
def update_course_prerequisite(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    course_id: int = Form(...),
    prerequisite_course_id: int | None = Form(default=None),
):
    service = AdvisingService(AdvisingRepository(db))
    service.update_course_prerequisite(
        user.id, course_id, prerequisite_course_id
    )
    return RedirectResponse(
        url=request.url_for("admin_degree_plan_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/admin/degree-plan/override/{override_id}")
def resolve_override_request(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    override_id: int,
    decision: str = Form(...),
):
    service = AdvisingService(AdvisingRepository(db))
    service.resolve_override(user.id, override_id, decision)
    return RedirectResponse(
        url=request.url_for("admin_degree_plan_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/app/advisor/queue/{audit_id}/note")
def add_advisor_note(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    audit_id: int,
    note_text: str = Form(...),
):
    service = AdvisingService(AdvisingRepository(db))
    service.add_advisor_note(audit_id, user.id, note_text)
    return RedirectResponse(
        url=request.url_for("advisor_queue_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/app/advisor/queue/{audit_id}/decision")
def decide_advisor_audit(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    audit_id: int,
    decision: str = Form(...),
):
    service = AdvisingService(AdvisingRepository(db))
    service.decide_audit(audit_id, decision)
    return RedirectResponse(
        url=request.url_for("advisor_queue_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/app/course-audit/submit", response_class=HTMLResponse)
def submit_course_audit(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    semester: str = Form(...),
    course_ids: list[int] = Form(default=[]),
):
    repository = AdvisingRepository(db)
    service = AdvisingService(repository)
    service.submit_audit(user.id, semester, course_ids)
    return RedirectResponse(
        url=request.url_for("course_audit_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )