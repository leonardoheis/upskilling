from collections.abc import Sequence

from pydantic import Field

from .base import DomainModel
from .path_template import PathTemplate


class Career(DomainModel):
    career_id: int | None = None
    name: str | None = None
    specialization: str | None = None
    path_templates: Sequence[PathTemplate] = Field(default_factory=list[PathTemplate])
