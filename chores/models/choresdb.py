from sqlalchemy import (
        Column,
        ForeignKey,
        Integer,
        String,
        Table,
        Text
)
from sqlalchemy.orm import (
        Mapped,
        declarative_base,
        relationship
)
from typing import Any, List, TYPE_CHECKING

# TODO: remove when sqlalchemy 2.0 types work properly
if  TYPE_CHECKING:
    from sqlalchemy.orm.decl_api import DeclarativeMeta
    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True
else:
    Base = declarative_base()


class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False, unique=True)
    tasks: Mapped[List["Assignments"]] = relationship("Assignments")

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    people: Mapped[List["Assignments"]] = relationship("Assignments")

class Assignments(Base):
    __tablename__ = 'assignments'

    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    people_id = Column(Integer, ForeignKey('people.id'), primary_key=True)
    counter = Column(Integer, default=0)

class Timers(Base):
    __tablename__ = 'timers'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    frequency = Column(Integer, default=72)
