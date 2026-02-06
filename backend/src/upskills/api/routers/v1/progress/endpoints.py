from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.api.dependencies import authenticated, require_permissions
from upskills.domain import User, UserCareerPath, UserPathAssignment, UserStepProgress
from upskills.services import ProgressService, TeamService

from .schemas import (
    DashboardStats,
    MenteeProgressSummary,
    UserCareerPathCreate,
    UserCareerPathDetailResponse,
    UserCareerPathResponse,
    UserCareerPathUpdate,
    UserPathAssignmentCreate,
    UserPathAssignmentDetailResponse,
    UserPathAssignmentResponse,
    UserPathAssignmentUpdate,
    UserStepProgressResponse,
    UserStepProgressUpdate,
)

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/dashboard")
@inject
async def get_dashboard(
    current_user: Annotated[User, Depends(authenticated)],
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> DashboardStats:
    result = await service.get_dashboard_stats(current_user.user_id)
    return DashboardStats.model_validate(result.model_dump())


@router.get("/career-paths")
@inject
async def get_my_career_paths(
    current_user: Annotated[User, Depends(authenticated)],
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserCareerPathDetailResponse]:
    results = await service.get_user_career_paths(current_user.user_id)
    return [UserCareerPathDetailResponse.model_validate(r.model_dump()) for r in results]


@router.get("/career-paths/{career_path_id}", dependencies=[Depends(authenticated)])
@inject
async def get_career_path(
    career_path_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathDetailResponse:
    result = await service.get_career_path(career_path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return UserCareerPathDetailResponse.model_validate(result.model_dump())


@router.post(
    "/career-paths", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("paths.assign"))]
)
@inject
async def assign_career_path(
    data: UserCareerPathCreate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathResponse:
    career_path = UserCareerPath(
        user_id=data.user_id,
        career_id=data.career_id,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    result = await service.assign_career_path(career_path)
    return UserCareerPathResponse.model_validate(result.model_dump())


@router.put("/career-paths/{career_path_id}", dependencies=[Depends(require_permissions("paths.assign"))])
@inject
async def update_career_path(
    career_path_id: int,
    data: UserCareerPathUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathResponse:
    career_path = UserCareerPath(
        start_date=data.start_date,
        end_date=data.end_date,
    )
    result = await service.update_career_path(career_path_id, career_path)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return UserCareerPathResponse.model_validate(result.model_dump())


@router.get("/career-paths/{career_path_id}/assignments", dependencies=[Depends(authenticated)])
@inject
async def get_path_assignments(
    career_path_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserPathAssignmentResponse]:
    results = await service.get_path_assignments(career_path_id)
    return [UserPathAssignmentResponse.model_validate(r.model_dump()) for r in results]


@router.post(
    "/assignments", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permissions("paths.assign"))]
)
@inject
async def assign_path(
    data: UserPathAssignmentCreate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    assignment = UserPathAssignment(
        user_career_path_id=data.user_career_path_id,
        path_template_id=data.path_template_id,
        start_date=data.start_date,
        deadline=data.deadline,
    )
    result = await service.assign_path(assignment)
    return UserPathAssignmentResponse.model_validate(result.model_dump())


@router.get("/assignments/{assignment_id}", dependencies=[Depends(authenticated)])
@inject
async def get_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentDetailResponse:
    result = await service.get_path_assignment(assignment_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentDetailResponse.model_validate(result.model_dump())


@router.put("/assignments/{assignment_id}", dependencies=[Depends(authenticated)])
@inject
async def update_assignment(
    assignment_id: int,
    data: UserPathAssignmentUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    assignment = UserPathAssignment(
        status=data.status.value if data.status else None,
        mentor_validation_status=data.mentor_validation_status.value if data.mentor_validation_status else None,
    )
    result = await service.update_assignment_status(assignment_id, assignment)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentResponse.model_validate(result.model_dump())


@router.get("/pending-validations", dependencies=[Depends(require_permissions("paths.validate"))])
@inject
async def get_pending_validations(
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserPathAssignmentDetailResponse]:
    results = await service.get_pending_validations()
    return [UserPathAssignmentDetailResponse.model_validate(r.model_dump()) for r in results]


@router.post("/assignments/{assignment_id}/approve", dependencies=[Depends(require_permissions("paths.validate"))])
@inject
async def approve_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    assignment = UserPathAssignment(mentor_validation_status="Approved")
    result = await service.update_assignment_status(assignment_id, assignment)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentResponse.model_validate(result.model_dump())


@router.post("/assignments/{assignment_id}/reject", dependencies=[Depends(require_permissions("paths.validate"))])
@inject
async def reject_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    assignment = UserPathAssignment(mentor_validation_status="Rejected")
    result = await service.update_assignment_status(assignment_id, assignment)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return UserPathAssignmentResponse.model_validate(result.model_dump())


@router.get("/assignments/{assignment_id}/steps", dependencies=[Depends(authenticated)])
@inject
async def get_step_progress(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserStepProgressResponse]:
    results = await service.get_step_progress(assignment_id)
    return [UserStepProgressResponse.model_validate(r.model_dump()) for r in results]


@router.put("/steps/{progress_id}", dependencies=[Depends(authenticated)])
@inject
async def update_step_progress(
    progress_id: int,
    data: UserStepProgressUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserStepProgressResponse:
    progress = UserStepProgress(
        status=data.status.value if data.status else None,
        progress_percent=data.progress_percent,
        planned_start_date=data.planned_start_date,
        planned_end_date=data.planned_end_date,
        actual_start_date=data.actual_start_date,
        actual_end_date=data.actual_end_date,
    )
    result = await service.update_step_progress(progress_id, progress)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step progress not found",
        )

    return UserStepProgressResponse.model_validate(result.model_dump())


@router.get("/team-progress")
@inject
async def get_team_progress(
    current_user: Annotated[User, Depends(authenticated)],
    team_service: Annotated[TeamService, Depends(Provide["team_service"])],
    progress_service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[MenteeProgressSummary]:
    teams = await team_service.get_teams_by_manager(current_user.user_id)

    member_ids: set[int] = set()
    for team in teams:
        if team.members:
            for member in team.members:
                if member.user_id is not None:
                    member_ids.add(member.user_id)

    if not member_ids:
        return []

    summaries = await progress_service.get_mentee_progress_summaries(list(member_ids))
    return [MenteeProgressSummary.model_validate(s.model_dump()) for s in summaries]
