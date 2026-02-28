from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.path_template.models import PathTemplate
    from upskills.repositories.user_career_path.models import UserCareerPath


class Career(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "careers"

    career_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    specialization: Mapped[str | None] = mapped_column(String(255))

    path_templates: Mapped[list["PathTemplate"]] = relationship(back_populates="career", lazy="selectin")
    user_career_paths: Mapped[list["UserCareerPath"]] = relationship(back_populates="career", lazy="selectin")
