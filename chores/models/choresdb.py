from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from typing import Any, List, TYPE_CHECKING

class Base(DeclarativeBase):
    pass

class People(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    tasks: Mapped[List["Assignments"]] = relationship("Assignments")


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    people: Mapped[List["Assignments"]] = relationship("Assignments")


class Assignments(Base):
    __tablename__ = "assignments"

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), primary_key=True)
    people_id: Mapped[int] = mapped_column(Integer, ForeignKey("people.id"), primary_key=True)
    counter: Mapped[int] = mapped_column(Integer, default=0)
    task: Mapped["Tasks"] = relationship("Tasks", back_populates="people")
    person: Mapped["People"] = relationship("People", back_populates="tasks")


class Timers(Base):
    __tablename__ = "timers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=72)
