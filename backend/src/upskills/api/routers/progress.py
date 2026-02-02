"""Progress tracking router."""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from upskills.core.dependencies import CurrentUser, require_permissions
from upskills.models.db.user import User
from upskills.models.domain.progress import (
    DashboardStats,
    MenteeProgressSummary,
    StepProgressUpdateInput,
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
from upskills.services.progress import ProgressService
from upskills.services.team import TeamService

router = APIRouter()


# === Dashboard ===


@router.get("/dashboard")
@inject
async def get_dashboard(
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> DashboardStats:
    """Get dashboard statistics for the current user."""
    return await service.get_dashboard_stats(current_user.user_id)


# === Career Paths ===


@router.get("/career-paths")
@inject
async def get_my_career_paths(
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserCareerPathDetailResponse]:
    """Get career paths for the current user."""
    return await service.get_user_career_paths(current_user.user_id)


@router.get("/career-paths/{career_path_id}")
@inject
async def get_career_path(
    career_path_id: int,
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserCareerPathDetailResponse:
    """Get a specific career path."""
    result = await service.get_career_path(career_path_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return result


@router.post(
    "/career-paths",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def assign_career_path(
    data: UserCareerPathCreate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
    _: Annotated[User, Depends(require_permissions("paths.assign"))],
) -> UserCareerPathResponse:
    """Assign a career path to a user (requires paths.assign permission)."""

    try:
        result = await service.assign_career_path(
            user_id=data.user_id,
            career_id=data.career_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put("/career-paths/{career_path_id}")
@inject
async def update_career_path(
    career_path_id: int,
    data: UserCareerPathUpdate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
    _: Annotated[User, Depends(require_permissions("paths.assign"))],
) -> UserCareerPathResponse:
    """Update a career path (requires paths.assign permission)."""
    result = await service.update_career_path(
        career_path_id,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career path not found",
        )

    return result


# === Path Assignments ===


@router.get(
    "/career-paths/{career_path_id}/assignments",
)
@inject
async def get_path_assignments(
    career_path_id: int,
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserPathAssignmentResponse]:
    """Get path assignments for a career path."""
    return await service.get_path_assignments(career_path_id)


@router.post(
    "/assignments",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def assign_path(
    data: UserPathAssignmentCreate,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
    _: Annotated[User, Depends(require_permissions("paths.assign"))],
) -> UserPathAssignmentResponse:
    """Assign a path to a user's career (requires paths.assign permission)."""

    try:
        result = await service.assign_path(
            user_career_path_id=data.user_career_path_id,
            path_template_id=data.path_template_id,
            start_date=data.start_date,
            deadline=data.deadline,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/assignments/{assignment_id}")
@inject
async def get_assignment(
    assignment_id: int,
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentDetailResponse:
    """Get a specific path assignment with details."""
    result = await service.get_path_assignment(assignment_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


@router.put("/assignments/{assignment_id}")
@inject
async def update_assignment(
    assignment_id: int,
    data: UserPathAssignmentUpdate,
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserPathAssignmentResponse:
    """Update a path assignment status."""
    result = await service.update_assignment_status(
        assignment_id,
        status=data.status.value if data.status else None,
        mentor_validation_status=data.mentor_validation_status.value
        if data.mentor_validation_status
        else None,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


# === Mentor Validation ===


@router.get("/pending-validations")
@inject
async def get_pending_validations(
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
    _: Annotated[User, Depends(require_permissions("paths.validate"))],
) -> list[UserPathAssignmentDetailResponse]:
    """Get all assignments pending mentor validation."""
    return await service.get_pending_validations()


@router.post("/assignments/{assignment_id}/approve")
@inject
async def approve_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
    _: Annotated[User, Depends(require_permissions("paths.validate"))],
) -> UserPathAssignmentResponse:
    """Approve a completed path assignment."""
    result = await service.update_assignment_status(
        assignment_id,
        mentor_validation_status="Approved",
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


@router.post("/assignments/{assignment_id}/reject")
@inject
async def reject_assignment(
    assignment_id: int,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
    _: Annotated[User, Depends(require_permissions("paths.validate"))],
) -> UserPathAssignmentResponse:
    """Reject a completed path assignment."""
    result = await service.update_assignment_status(
        assignment_id,
        mentor_validation_status="Rejected",
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return result


# === Step Progress ===


@router.get(
    "/assignments/{assignment_id}/steps",
)
@inject
async def get_step_progress(
    assignment_id: int,
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[UserStepProgressResponse]:
    """Get step progress for an assignment."""
    return await service.get_step_progress(assignment_id)


@router.put("/steps/{progress_id}")
@inject
async def update_step_progress(
    progress_id: int,
    data: UserStepProgressUpdate,
    current_user: CurrentUser,
    service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> UserStepProgressResponse:
    """Update step progress."""
    input_data = StepProgressUpdateInput(
        status=data.status.value if data.status else None,
        progress_percent=data.progress_percent,
        planned_start_date=data.planned_start_date,
        planned_end_date=data.planned_end_date,
        actual_start_date=data.actual_start_date,
        actual_end_date=data.actual_end_date,
    )
    result = await service.update_step_progress(progress_id, input_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step progress not found",
        )

    return result


# === Team Progress (for mentors) ===


@router.get("/team-progress")
@inject
async def get_team_progress(
    current_user: CurrentUser,
    team_service: Annotated[TeamService, Depends(Provide["team_service"])],
    progress_service: Annotated[ProgressService, Depends(Provide["progress_service"])],
) -> list[MenteeProgressSummary]:
    """Get progress summaries for mentees in teams managed by current user."""

    # Get teams managed by current user
    teams = await team_service.get_teams_by_manager(current_user.user_id)

    # Collect all unique member IDs
    member_ids: set[int] = set()
    for team in teams:
        member_ids.update(member.user_id for member in team.members)

    if not member_ids:
        return []

    return await progress_service.get_mentee_progress_summaries(list(member_ids))
