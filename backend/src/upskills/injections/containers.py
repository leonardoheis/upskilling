from dependency_injector import containers, providers

from upskills.db import SQLiteProvider
from upskills.repositories import (
    CareerRepository,
    LogEntryRepository,
    PathStepRepository,
    PathTemplateRepository,
    RoleRepository,
    TeamRepository,
    UserCareerPathRepository,
    UserPathAssignmentRepository,
    UserRepository,
    UserStepProgressRepository,
)
from upskills.services import (
    AuthService,
    CareerService,
    LogbookService,
    PathStepService,
    PathTemplateService,
    ProgressService,
    TeamService,
    UserService,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_provider = providers.Singleton(
        SQLiteProvider,
        db_path=config["database_path"],
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
