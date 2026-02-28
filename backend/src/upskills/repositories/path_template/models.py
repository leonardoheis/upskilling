from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from upskills.repositories.base import Base

if TYPE_CHECKING:
    from upskills.repositories.career.models import Career
    from upskills.repositories.user_path_assignment.models import UserPathAssignment


class PathTemplate(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "path_templates"

    path_template_id: Mapped[int] = mapped_column(primary_key=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.career_id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    duration_hours: Mapped[int] = mapped_column()
    default_start_offset_days: Mapped[int | None] = mapped_column()
    default_deadline_offset_days: Mapped[int | None] = mapped_column()

    career: Mapped["Career"] = relationship(back_populates="path_templates")
    steps: Mapped[list["PathTemplateStep"]] = relationship(
        back_populates="path_template", lazy="selectin", order_by="PathTemplateStep.step_order"
    )
    assignments: Mapped[list["UserPathAssignment"]] = relationship(back_populates="path_template", lazy="selectin")


class PathTemplateStep(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "path_template_steps"

    step_id: Mapped[int] = mapped_column(primary_key=True)
    path_template_id: Mapped[int] = mapped_column(ForeignKey("path_templates.path_template_id"))
    step_order: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    duration_hours: Mapped[int | None] = mapped_column()
    course_link: Mapped[str | None] = mapped_column(String(500))

    path_template: Mapped["PathTemplate"] = relationship(back_populates="steps")
    dependencies: Mapped[list["PathStepDependency"]] = relationship(
        back_populates="step",
        foreign_keys="PathStepDependency.step_id",
        lazy="selectin",
    )


class PathStepDependency(Base):  # pylint: disable=too-few-public-methods R0903
    __tablename__ = "path_step_dependencies"

    step_id: Mapped[int] = mapped_column(ForeignKey("path_template_steps.step_id"), primary_key=True)
    depends_on_step_id: Mapped[int] = mapped_column(ForeignKey("path_template_steps.step_id"), primary_key=True)

    step: Mapped["PathTemplateStep"] = relationship(
        back_populates="dependencies",
        foreign_keys=[step_id],
    )
    depends_on_step: Mapped["PathTemplateStep"] = relationship(
        foreign_keys=[depends_on_step_id],
    )
