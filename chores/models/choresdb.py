from typing import List

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy


class Base(DeclarativeBase):
    """Base declarative model."""


db = SQLAlchemy(model_class=Base)


class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    tasks: Mapped[List["Assignments"]] = relationship(
        "Assignments",
        back_populates="person",
        cascade="all, delete-orphan",
    )


class Tasks(db.Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    people: Mapped[List["Assignments"]] = relationship("Assignments", back_populates="task")


class Assignments(db.Model):
    __tablename__ = "assignments"

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), primary_key=True)
    people_id: Mapped[int] = mapped_column(Integer, ForeignKey("people.id"), primary_key=True)
    counter: Mapped[int] = mapped_column(Integer, default=0)
    task: Mapped["Tasks"] = relationship("Tasks", back_populates="people")
    person: Mapped["People"] = relationship("People", back_populates="tasks")


class AutoNags(db.Model):
    __tablename__ = "autonags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=72)
