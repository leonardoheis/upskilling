"""Progress tracking services."""

from datetime import date
from typing import Any

from dependency_injector.wiring import Provide, inject

from upskills.models.db.progress import UserCareerPath, UserPathAssignment, UserStepProgress
from upskills.models.domain.career import PathStepResponse, PathTemplateResponse
from upskills.models.domain.progress import (
    DashboardStats,
    MenteeProgressSummary,
    StepProgressUpdateInput,
    UserCareerPathDetailResponse,
    UserCareerPathResponse,
    UserPathAssignmentDetailResponse,
    UserPathAssignmentResponse,
    UserStepProgressResponse,
)
from upskills.repositories.path_template import PathTemplateRepository
from upskills.repositories.user import UserRepository
from upskills.repositories.user_career_path import UserCareerPathRepository
from upskills.repositories.user_path_assignment import UserPathAssignmentRepository
from upskills.repositories.user_step_progress import UserStepProgressRepository


class ProgressService:
    """Service for progress tracking operations."""

    @inject
    def __init__(
        self,
        career_path_repository: UserCareerPathRepository = Provide["user_career_path_repository"],
        assignment_repository: UserPathAssignmentRepository = Provide["user_path_assignment_repository"],
        step_progress_repository: UserStepProgressRepository = Provide["user_step_progress_repository"],
        user_repository: UserRepository = Provide["user_repository"],
        path_template_repository: PathTemplateRepository = Provide["path_template_repository"],
    ) -> None:
        self._career_path_repository = career_path_repository
        self._assignment_repository = assignment_repository
        self._step_progress_repository = step_progress_repository
        self._user_repository = user_repository
        self._path_template_repository = path_template_repository

    # === User Career Paths ===

    async def get_user_career_paths(self, user_id: int) -> list[UserCareerPathDetailResponse]:
        """Get all career paths for a user."""
        paths = await self._career_path_repository.get_by_user(user_id)
        return [await self._career_path_to_detail_response(p) for p in paths]

    async def get_career_path(
        self, user_career_path_id: int
    ) -> UserCareerPathDetailResponse | None:
        """Get a specific career path."""
        path = await self._career_path_repository.get_by_id(user_career_path_id)
        if not path:
            return None
        return await self._career_path_to_detail_response(path)

    async def assign_career_path(
        self,
        user_id: int,
        career_id: int,
        start_date: date,
        end_date: date,
    ) -> UserCareerPathResponse:
        """Assign a career path to a user."""
        # Verify user exists
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            msg = "User not found"
            raise ValueError(msg)

        path = await self._career_path_repository.create({
            "user_id": user_id,
            "career_id": career_id,
            "start_date": start_date,
            "end_date": end_date,
            "overall_progress_percent": 0,
        })

        return self._career_path_to_response(path)

    async def update_career_path(
        self,
        user_career_path_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> UserCareerPathResponse | None:
        """Update a career path."""
        path = await self._career_path_repository.get_by_id(user_career_path_id)
        if not path:
            return None

        update_data: dict[str, Any] = {}
        if start_date:
            update_data["start_date"] = start_date
        if end_date:
            update_data["end_date"] = end_date

        if update_data:
            path = await self._career_path_repository.update(path, update_data)

        return self._career_path_to_response(path)

    # === Path Assignments ===

    async def get_path_assignments(
        self, user_career_path_id: int
    ) -> list[UserPathAssignmentResponse]:
        """Get all path assignments for a career path."""
        assignments = await self._assignment_repository.get_by_career_path(user_career_path_id)
        return [self._assignment_to_response(a) for a in assignments]

    async def get_path_assignment(
        self, assignment_id: int
    ) -> UserPathAssignmentDetailResponse | None:
        """Get a specific path assignment with details."""
        assignment = await self._assignment_repository.get_by_id(assignment_id)
        if not assignment:
            return None
        return await self._assignment_to_detail_response(assignment)

    async def assign_path(
        self,
        user_career_path_id: int,
        path_template_id: int,
        start_date: date,
        deadline: date,
    ) -> UserPathAssignmentResponse:
        """Assign a path to a user's career."""
        # Verify career path exists
        career_path = await self._career_path_repository.get_by_id(user_career_path_id)
        if not career_path:
            msg = "Career path not found"
            raise ValueError(msg)

        # Verify path template exists
        template = await self._path_template_repository.get_by_id(path_template_id)
        if not template:
            msg = "Path template not found"
            raise ValueError(msg)

        assignment = await self._assignment_repository.create({
            "user_career_path_id": user_career_path_id,
            "path_template_id": path_template_id,
            "start_date": start_date,
            "deadline": deadline,
            "status": "Pending",
            "progress_percent": 0,
            "mentor_validation_status": "Pending",
        })

        # Initialize step progress for all steps
        if template.steps:
            for step in template.steps:
                await self._step_progress_repository.create({
                    "user_path_assignment_id": assignment.user_path_assignment_id,
                    "step_id": step.step_id,
                    "status": "Pending",
                    "progress_percent": 0,
                })

        return self._assignment_to_response(assignment)

    async def update_assignment_status(
        self,
        assignment_id: int,
        status: str | None = None,
        mentor_validation_status: str | None = None,
    ) -> UserPathAssignmentResponse | None:
        """Update a path assignment status."""
        assignment = await self._assignment_repository.get_by_id(assignment_id)
        if not assignment:
            return None

        update_data: dict[str, Any] = {}
        if status:
            update_data["status"] = status
        if mentor_validation_status:
            update_data["mentor_validation_status"] = mentor_validation_status

        if update_data:
            assignment = await self._assignment_repository.update(assignment, update_data)

        # Recalculate career path progress
        await self._recalculate_career_progress(assignment.user_career_path_id)

        return self._assignment_to_response(assignment)

    async def get_pending_validations(self) -> list[UserPathAssignmentDetailResponse]:
        """Get all assignments pending mentor validation."""
        assignments = await self._assignment_repository.get_pending_validation()
        return [await self._assignment_to_detail_response(a) for a in assignments]

    # === Step Progress ===

    async def get_step_progress(self, assignment_id: int) -> list[UserStepProgressResponse]:
        """Get step progress for an assignment."""
        progress_list = await self._step_progress_repository.get_by_assignment(assignment_id)
        return [self._step_progress_to_response(p) for p in progress_list]

    async def update_step_progress(
        self,
        progress_id: int,
        data: StepProgressUpdateInput,
    ) -> UserStepProgressResponse | None:
        """Update step progress."""
        progress = await self._step_progress_repository.get_by_id(progress_id)
        if not progress:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            progress = await self._step_progress_repository.update(progress, update_data)

        # Recalculate assignment progress
        await self._recalculate_assignment_progress(progress.user_path_assignment_id)

        return self._step_progress_to_response(progress)

    # === Dashboard ===

    async def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        """Get dashboard statistics for a user."""
        career_path = await self._career_path_repository.get_active_for_user(user_id)

        if not career_path:
            return DashboardStats(
                current_career=None,
                current_path=None,
                current_path_progress=0,
                paths_remaining=0,
                overall_progress=0,
                skills_obtained=0,
            )

        # Find current in-progress path
        current_path_name = None
        current_path_progress = 0
        paths_remaining = 0
        skills_obtained = 0

        if career_path.path_assignments:
            for assignment in career_path.path_assignments:
                if assignment.status == "In Progress":
                    current_path_name = (
                        assignment.path_template.name if assignment.path_template else None
                    )
                    current_path_progress = assignment.progress_percent
                elif assignment.status == "Pending":
                    paths_remaining += 1
                elif assignment.mentor_validation_status == "Approved":
                    skills_obtained += 1

        return DashboardStats(
            current_career=career_path.career.name if career_path.career else None,
            current_path=current_path_name,
            current_path_progress=current_path_progress,
            paths_remaining=paths_remaining,
            overall_progress=career_path.overall_progress_percent,
            skills_obtained=skills_obtained,
        )

    async def get_mentee_progress_summaries(
        self, team_user_ids: list[int]
    ) -> list[MenteeProgressSummary]:
        """Get progress summaries for mentees."""
        summaries = []

        for user_id in team_user_ids:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                continue

            career_path = await self._career_path_repository.get_active_for_user(user_id)
            if not career_path:
                continue

            completed, total = await self._assignment_repository.count_completed_for_career_path(
                career_path.user_career_path_id
            )

            # Count pending validations
            pending = 0
            if career_path.path_assignments:
                for a in career_path.path_assignments:
                    if a.status == "Completed" and a.mentor_validation_status == "Pending":
                        pending += 1

            summaries.append(
                MenteeProgressSummary(
                    user_id=user.user_id,
                    full_name=user.full_name,
                    email=user.email,
                    career_name=career_path.career.name if career_path.career else "Unknown",
                    start_date=career_path.start_date,
                    end_date=career_path.end_date,
                    overall_progress_percent=career_path.overall_progress_percent,
                    paths_completed=completed,
                    paths_total=total,
                    pending_validation=pending,
                )
            )

        return summaries

    # === Private Helpers ===

    async def _recalculate_assignment_progress(self, assignment_id: int) -> None:
        """Recalculate progress percentage for an assignment."""
        assignment = await self._assignment_repository.get_by_id(assignment_id)
        if not assignment or not assignment.step_progress:
            return

        total_steps = len(assignment.step_progress)
        if total_steps == 0:
            return

        total_progress = sum(sp.progress_percent for sp in assignment.step_progress)
        new_progress = total_progress // total_steps

        # Check if all steps are completed
        all_completed = all(sp.status == "Completed" for sp in assignment.step_progress)
        new_status = (
            "Completed"
            if all_completed
            else (
                "In Progress"
                if any(sp.status != "Pending" for sp in assignment.step_progress)
                else "Pending"
            )
        )

        await self._assignment_repository.update(
            assignment,
            {
                "progress_percent": new_progress,
                "status": new_status,
            },
        )

        # Recalculate career path progress
        await self._recalculate_career_progress(assignment.user_career_path_id)

    async def _recalculate_career_progress(self, career_path_id: int) -> None:
        """Recalculate overall progress for a career path."""
        career_path = await self._career_path_repository.get_by_id(career_path_id)
        if not career_path or not career_path.path_assignments:
            return

        total_assignments = len(career_path.path_assignments)
        if total_assignments == 0:
            return

        total_progress = sum(a.progress_percent for a in career_path.path_assignments)
        new_progress = total_progress // total_assignments

        await self._career_path_repository.update(
            career_path,
            {
                "overall_progress_percent": new_progress,
            },
        )

    @staticmethod
    def _career_path_to_response(path: UserCareerPath) -> UserCareerPathResponse:
        """Convert UserCareerPath to response."""
        return UserCareerPathResponse(
            user_career_path_id=path.user_career_path_id,
            user_id=path.user_id,
            career_id=path.career_id,
            start_date=path.start_date,
            end_date=path.end_date,
            overall_progress_percent=path.overall_progress_percent,
        )

    async def _career_path_to_detail_response(
        self, path: UserCareerPath
    ) -> UserCareerPathDetailResponse:
        """Convert UserCareerPath to detailed response."""
        assignments = []
        if path.path_assignments:
            assignments = [self._assignment_to_response(a) for a in path.path_assignments]

        return UserCareerPathDetailResponse(
            user_career_path_id=path.user_career_path_id,
            user_id=path.user_id,
            career_id=path.career_id,
            start_date=path.start_date,
            end_date=path.end_date,
            overall_progress_percent=path.overall_progress_percent,
            career_name=path.career.name if path.career else "Unknown",
            career_specialization=path.career.specialization if path.career else None,
            path_assignments=assignments,
        )

    @staticmethod
    def _assignment_to_response(assignment: UserPathAssignment) -> UserPathAssignmentResponse:
        """Convert UserPathAssignment to response."""
        return UserPathAssignmentResponse(
            user_path_assignment_id=assignment.user_path_assignment_id,
            user_career_path_id=assignment.user_career_path_id,
            path_template_id=assignment.path_template_id,
            start_date=assignment.start_date,
            deadline=assignment.deadline,
            status=assignment.status,
            progress_percent=assignment.progress_percent,
            mentor_validation_status=assignment.mentor_validation_status,
        )

    async def _assignment_to_detail_response(
        self, assignment: UserPathAssignment
    ) -> UserPathAssignmentDetailResponse:
        """Convert UserPathAssignment to detailed response."""
        step_progress = []
        if assignment.step_progress:
            step_progress = [self._step_progress_to_response(sp) for sp in assignment.step_progress]

        path_template = None
        if assignment.path_template:
            path_template = PathTemplateResponse(
                path_template_id=assignment.path_template.path_template_id,
                career_id=assignment.path_template.career_id,
                name=assignment.path_template.name,
                description=assignment.path_template.description,
                duration_hours=assignment.path_template.duration_hours,
                default_start_offset_days=assignment.path_template.default_start_offset_days,
                default_deadline_offset_days=assignment.path_template.default_deadline_offset_days,
            )

        return UserPathAssignmentDetailResponse(
            user_path_assignment_id=assignment.user_path_assignment_id,
            user_career_path_id=assignment.user_career_path_id,
            path_template_id=assignment.path_template_id,
            start_date=assignment.start_date,
            deadline=assignment.deadline,
            status=assignment.status,
            progress_percent=assignment.progress_percent,
            mentor_validation_status=assignment.mentor_validation_status,
            path_template=path_template,
            step_progress=step_progress,
        )

    @staticmethod
    def _step_progress_to_response(progress: UserStepProgress) -> UserStepProgressResponse:
        """Convert UserStepProgress to response."""
        step = None
        if progress.step:
            step = PathStepResponse(
                step_id=progress.step.step_id,
                path_template_id=progress.step.path_template_id,
                step_order=progress.step.step_order,
                name=progress.step.name,
                description=progress.step.description,
                duration_hours=progress.step.duration_hours,
                course_link=progress.step.course_link,
                dependencies=[],
            )

        return UserStepProgressResponse(
            user_step_progress_id=progress.user_step_progress_id,
            user_path_assignment_id=progress.user_path_assignment_id,
            step_id=progress.step_id,
            status=progress.status,
            progress_percent=progress.progress_percent,
            planned_start_date=progress.planned_start_date,
            planned_end_date=progress.planned_end_date,
            actual_start_date=progress.actual_start_date,
            actual_end_date=progress.actual_end_date,
            updated_at=progress.updated_at,
            step=step,
        )
