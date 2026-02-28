from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count

from upskills.domain import PathStep as PathStepDomain
from upskills.domain import PathTemplate as PathTemplateDomain
from upskills.domain import UserPathAssignment as UserPathAssignmentDomain
from upskills.domain import UserStepProgress as UserStepProgressDomain
from upskills.repositories.base import BaseRepository
from upskills.repositories.path_template.models import PathTemplate
from upskills.repositories.user_career_path.models import UserCareerPath

from .models import UserPathAssignment


class UserPathAssignmentRepository(BaseRepository[UserPathAssignment]):
    async def get_by_id(self, id_value: int, id_column: str = "user_path_assignment_id") -> UserPathAssignment | None:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserPathAssignment)
                .options(
                    selectinload(UserPathAssignment.path_template).selectinload(PathTemplate.steps),
                    selectinload(UserPathAssignment.step_progress),
                )
                .where(UserPathAssignment.user_path_assignment_id == id_value)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_career_path(self, user_career_path_id: int) -> list[UserPathAssignment]:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserPathAssignment)
                .options(
                    selectinload(UserPathAssignment.path_template),
                    selectinload(UserPathAssignment.step_progress),
                )
                .where(UserPathAssignment.user_career_path_id == user_career_path_id)
                .order_by(UserPathAssignment.start_date)
            )
            result = await session.execute(stmt)
            return list[UserPathAssignment](result.scalars().all())

    async def get_pending_validation(self, _mentor_user_id: int | None = None) -> list[UserPathAssignment]:
        async with self._db_provider.session() as session:
            stmt = (
                select(UserPathAssignment)
                .options(
                    selectinload(UserPathAssignment.path_template),
                    selectinload(UserPathAssignment.user_career_path).selectinload(UserCareerPath.user),
                    selectinload(UserPathAssignment.step_progress),
                )
                .where(
                    UserPathAssignment.status == "Completed",
                    UserPathAssignment.mentor_validation_status == "Pending",
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count_completed_for_career_path(self, user_career_path_id: int) -> tuple[int, int]:
        async with self._db_provider.session() as session:
            total_stmt = (
                select(count())  # pylint: disable=no-member E1101
                .select_from(UserPathAssignment)
                .where(UserPathAssignment.user_career_path_id == user_career_path_id)
            )
            completed_stmt = (
                select(count())  # pylint: disable=no-member E1101
                .select_from(UserPathAssignment)
                .where(
                    UserPathAssignment.user_career_path_id == user_career_path_id,
                    UserPathAssignment.mentor_validation_status == "Approved",
                )
            )

            total_result = await session.execute(total_stmt)
            completed_result = await session.execute(completed_stmt)

            return completed_result.scalar() or 0, total_result.scalar() or 0

    @staticmethod
    def to_domain(assignment: UserPathAssignment, *, include_details: bool = False) -> UserPathAssignmentDomain:
        step_progress = []
        path_template = None

        if include_details:
            if assignment.step_progress:
                step_progress = [
                    UserStepProgressDomain(
                        user_step_progress_id=sp.user_step_progress_id,
                        user_path_assignment_id=sp.user_path_assignment_id,
                        step_id=sp.step_id,
                        status=sp.status,
                        progress_percent=sp.progress_percent,
                        planned_start_date=sp.planned_start_date,
                        planned_end_date=sp.planned_end_date,
                        actual_start_date=sp.actual_start_date,
                        actual_end_date=sp.actual_end_date,
                        step=PathStepDomain(
                            step_id=sp.step.step_id,
                            path_template_id=sp.step.path_template_id,
                            step_order=sp.step.step_order,
                            name=sp.step.name,
                            description=sp.step.description,
                            duration_hours=sp.step.duration_hours,
                            course_link=sp.step.course_link,
                        )
                        if sp.step
                        else None,
                    )
                    for sp in assignment.step_progress
                ]

            if assignment.path_template:
                path_template = PathTemplateDomain(
                    path_template_id=assignment.path_template.path_template_id,
                    career_id=assignment.path_template.career_id,
                    name=assignment.path_template.name,
                    description=assignment.path_template.description,
                    duration_hours=assignment.path_template.duration_hours,
                    default_start_offset_days=assignment.path_template.default_start_offset_days,
                    default_deadline_offset_days=assignment.path_template.default_deadline_offset_days,
                )

        return UserPathAssignmentDomain(
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
