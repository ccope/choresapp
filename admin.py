#!/usr/bin/env python3
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import Session
from tap import Tap
from typing import Any, Optional
from typing_extensions import Literal

from chores.models.choresdb import Assignments, People, Tasks


load_dotenv()
g: Any = {}


def assign(args: Tap):
    if args.action == 'add':
        assign_task(args.person, args.task)
    elif args.action == 'delete':
        unassign_task(args.person, args.task)


def person(args: Tap):
    if args.action == 'add':
        add_person(args.name)
    elif args.action == 'delete':
        del_person(args.name)


def task(args: Tap):
    if args.action == 'add':
        add_task(args.name)
    elif args.action == 'delete':
        del_task(args.name)


def add_task(name: str, description: Optional[str] = None):
    if not description:
        description = input("Enter the task description: ")
    new_task = Tasks(name=name, description=description)
    with Session(g['engine']) as session:
        tasks = session.execute(select(Tasks).where(Tasks.name == name)).fetchall()
        if len(tasks) > 0:
            print("Task {} already exists, skpping".format(name))
        else:
            session.add(new_task)
            session.commit()


def del_task(name: str):
    print("TODO")
    raise Exception("unimplemented!")


def assign_task(person_name: str, task_name: str):
    #TODO: set counter for newbies to highest of current asssignees
    with Session(g['engine']) as session:
        p_st = select(People).where(People.name == person_name)
        t_st = select(Tasks).where(Tasks.name == task_name)
        person = session.execute(p_st).scalars().one()
        task = session.execute(t_st).scalars().one()
        a_st = select(Assignments).where(and_(Assignments.people_id == person.id, Assignments.task_id == task.id))
        a_result = session.execute(a_st).fetchone()
        if a_result:
            print("{} is already assigned to {}".format(person_name, task_name))
            return
        a = Assignments()
        a.task = task
        person.tasks.append(a)
        session.commit()
        f_st = select(Assignments).where(and_(Assignments.people_id == person.id, Assignments.task_id == task.id))
        f_result = session.execute(f_st).scalars().one()
        print("Assigned {} to {}".format(person_name, task_name))


def unassign_task(name: str, task: str):
    print("TODO")
    raise Exception("unimplemented!")


def add_person(name: str, email: Optional[str] = None):
    if not email:
        email = input("Enter the person's email address: ")
    newbie = People(name=name, email=email)
    with Session(g['engine']) as session:
        session.add(newbie)
        session.commit()


def del_person(name: str):
    print("TODO")
    raise Exception("unimplemented!")


class AssignmentSubparser(Tap):
    action: Literal['add', 'delete']
    person: str
    task: str

    def configure(self):
        self.set_defaults(func=assign)


class PersonSubparser(Tap):
    action: Literal['add', 'delete']
    name: str

    def configure(self):
        self.set_defaults(func=person)


class TaskSubparser(Tap):
    action: Literal['add', 'delete']
    name: str

    def configure(self):
        self.set_defaults(func=task)


class SimpleArgumentParser(Tap):
    def configure(self):
        self.add_subparsers(help='sub-command help')
        self.add_subparser('assign', AssignmentSubparser, help='assignment help')
        self.add_subparser('person', PersonSubparser, help='person help')
        self.add_subparser('task', TaskSubparser, help='task help')


if __name__ == '__main__':
    args = SimpleArgumentParser().parse_args()
    g['engine'] = create_engine(os.environ['DBURI'], echo=True, future=True)
    args.func(args)
