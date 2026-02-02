from dependency_injector import containers, providers

from upskills.db.sqlite import SQLiteProvider
from upskills.repositories.career import CareerRepository
from upskills.repositories.log_entry import LogEntryRepository
from upskills.repositories.path_step import PathStepRepository
from upskills.repositories.path_template import PathTemplateRepository
from upskills.repositories.role import RoleRepository
from upskills.repositories.team import TeamRepository
from upskills.repositories.user import UserRepository
from upskills.repositories.user_career_path import UserCareerPathRepository
from upskills.repositories.user_path_assignment import UserPathAssignmentRepository
from upskills.repositories.user_step_progress import UserStepProgressRepository
from upskills.services.auth import AuthService
from upskills.services.career import CareerService
from upskills.services.logbook import LogbookService
from upskills.services.path_step import PathStepService
from upskills.services.path_template import PathTemplateService
from upskills.services.progress import ProgressService
from upskills.services.team import TeamService
from upskills.services.user import UserService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_provider = providers.Singleton(
        SQLiteProvider,
        db_path=config.database_path,
    )

    # Repositories
    user_repository = providers.Factory(UserRepository)
    role_repository = providers.Factory(RoleRepository)
    team_repository = providers.Factory(TeamRepository)
    career_repository = providers.Factory(CareerRepository)
    path_template_repository = providers.Factory(PathTemplateRepository)
    path_step_repository = providers.Factory(PathStepRepository)
    user_career_path_repository = providers.Factory(UserCareerPathRepository)
    user_path_assignment_repository = providers.Factory(UserPathAssignmentRepository)
    user_step_progress_repository = providers.Factory(UserStepProgressRepository)
    log_entry_repository = providers.Factory(LogEntryRepository)

    # Services
    user_service = providers.Factory(UserService)
    auth_service = providers.Factory(AuthService)
    team_service = providers.Factory(TeamService)
    career_service = providers.Factory(CareerService)
    path_template_service = providers.Factory(PathTemplateService)
    path_step_service = providers.Factory(PathStepService)
    progress_service = providers.Factory(ProgressService)
    logbook_service = providers.Factory(LogbookService)
