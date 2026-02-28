from dataclasses import dataclass

from dependency_injector.wiring import Provide

from upskills.domain import PathTemplate
from upskills.repositories import CareerRepository, PathTemplateRepository


@dataclass
class PathTemplateService:
    path_template_repository: PathTemplateRepository = Provide["path_template_repository"]
    career_repository: CareerRepository = Provide["career_repository"]

    async def get(self, path_template_id: int) -> PathTemplate | None:
        path_template = await self.path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not path_template:
            return None
        return self.path_template_repository.to_domain(path_template)

    async def get_all(
        self, *, skip: int = 0, limit: int = 100, career_id: int | None = None
    ) -> tuple[list[PathTemplate], int]:
        if career_id:
            paths = await self.path_template_repository.get_by_career(career_id)
            return paths, len(paths)

        paths = await self.path_template_repository.get_all_with_details(skip=skip, limit=limit)
        total = await self.path_template_repository.count()
        return paths, total

    async def create(self, path_template_: PathTemplate) -> PathTemplate:
        career = await self.career_repository.get_by_id(path_template_.career_id, id_column="career_id")
        if not career:
            msg = "Career not found"
            raise ValueError(msg)

        path_template = await self.path_template_repository.create(path_template_)
        return self.path_template_repository.to_domain(path_template)

    async def update(self, path_template_id: int, path_template_: PathTemplate) -> PathTemplate | None:
        path_template = await self.path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not path_template:
            return None
        updated_path_template = await self.path_template_repository.update(path_template, path_template_)
        return self.path_template_repository.to_domain(updated_path_template)

    async def delete(self, path_template_id: int) -> bool:
        path_template = await self.path_template_repository.get_by_id(path_template_id, id_column="path_template_id")
        if not path_template:
            return False
        await self.path_template_repository.delete(path_template)
        return True
