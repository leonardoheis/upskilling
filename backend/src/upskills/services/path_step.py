from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import PathStep
from upskills.repositories import PathStepRepository, PathTemplateRepository


@dataclass
class PathStepService:
    path_step_repository: PathStepRepository = Provide["path_step_repository"]
    path_template_repository: PathTemplateRepository = Provide["path_template_repository"]

    async def get(self, step_id: int) -> PathStep | None:
        step = await self.path_step_repository.get_by_id(step_id)
        if not step:
            return None
        return self.path_step_repository.to_domain(step)

    async def get_for_path(self, path_template_id: int) -> list[PathStep]:
        steps = await self.path_step_repository.get_by_path_template(path_template_id)
        return [self.path_step_repository.to_domain(s) for s in steps]

    async def create(self, path_step_: PathStep) -> PathStep:
        path = await self.path_template_repository.get_by_id(path_step_.path_template_id, id_column="path_template_id")
        if not path:
            msg = "Path template not found"
            raise ValueError(msg)

        path_step = await self.path_step_repository.create(path_step_)
        return self.path_step_repository.to_domain(path_step)

    async def update(self, step_id: int, path_step_: PathStep) -> PathStep | None:
        path_step = await self.path_step_repository.get_by_id(step_id, id_column="step_id")
        if not path_step:
            return None
        updated_path_step = await self.path_step_repository.update(path_step, path_step_)
        return self.path_step_repository.to_domain(updated_path_step)

    async def delete(self, step_id: int) -> bool:
        path_step = await self.path_step_repository.get_by_id(step_id, id_column="step_id")
        if not path_step:
            return False
        await self.path_step_repository.delete(path_step)
        return True

    async def add_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self.path_step_repository.add_dependency(step_id, depends_on_step_id)
        return True

    async def remove_dependency(self, step_id: int, depends_on_step_id: int) -> bool:
        await self.path_step_repository.remove_dependency(step_id, depends_on_step_id)
        return True
