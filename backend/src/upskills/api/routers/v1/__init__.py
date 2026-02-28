from fastapi import APIRouter, Depends

from upskills.api.dependencies import authenticated

from .auth import router as auth_router
from .careers import router as careers_router
from .logbook import router as logbook_router
from .path_steps import router as path_steps_router
from .path_templates import router as path_templates_router
from .progress import router as progress_router
from .teams import router as teams_router
from .users import router as users_router

router = APIRouter(prefix="/api/v1", dependencies=[Depends(authenticated)])

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(teams_router)
router.include_router(careers_router)
router.include_router(path_templates_router)
router.include_router(path_steps_router)
router.include_router(progress_router)
router.include_router(logbook_router)

__all__ = ["router"]
