import os

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import Session
from sqlalchemy.future import Engine
from typing import Optional

from chores.models.choresdb import Assignments, People, Tasks


class Manager:
    def __init__(self, engine: Engine):
        self.engine = engine or create_engine(os.environ["DBURI"], echo=True, future=True)

    def add_task(self, name: str, description: Optional[str] = None):
        if not description:
            description = input("Enter the task description: ")
        new_task = Tasks(name=name, description=description)
        with Session(self.engine) as session:
            tasks = session.execute(select(Tasks).where(Tasks.name == name)).fetchall()
            if len(tasks) > 0:
                print("Task {} already exists, skpping".format(name))
            else:
                session.add(new_task)
                session.commit()

    def del_task(self, name: str):
        print("TODO")
        raise Exception("unimplemented!")

    def assign_task(self, person_name: str, task_name: str):
        # TODO: set counter for newbies to highest of current asssignees
        with Session(self.engine) as session:
            p_st = select(People).where(People.name == person_name)
            t_st = select(Tasks).where(Tasks.name == task_name)
            person = session.execute(p_st).scalars().one()
            task = session.execute(t_st).scalars().one()
            a_st = select(Assignments).where(
                and_(Assignments.people_id == person.id, Assignments.task_id == task.id)
            )
            a_result = session.execute(a_st).fetchone()
            if a_result:
                print("{} is already assigned to {}".format(person_name, task_name))
                return
            a = Assignments()
            a.task = task
            person.tasks.append(a)
            session.commit()
            print("Assigned {} to {}".format(person_name, task_name))

    def unassign_task(self, name: str, task: str):
        print("TODO")
        raise Exception("unimplemented!")

    def add_person(self, name: str, email: Optional[str] = None):
        if not email:
            email = input("Enter the person's email address: ")
        newbie = People(name=name, email=email)
        with Session(self.engine) as session:
            session.add(newbie)
            session.commit()

    def del_person(self, name: str):
        print("TODO")
        raise Exception("unimplemented!")
