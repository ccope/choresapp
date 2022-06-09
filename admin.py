#!/usr/bin/env python3
from dotenv import load_dotenv
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from tap import Tap
from typing_extensions import Literal

from chores.manager import Manager
from chores.models.choresdb import Assignments


load_dotenv()
MANAGER: Manager = Manager()


def assign(args: Tap):
    if args.action == "add":
        MANAGER.assign_task(args.person, args.task)
    elif args.action == "delete":
        MANAGER.unassign_task(args.person, args.task)


def person(args: Tap):
    if args.action == "add":
        MANAGER.add_person(args.name)
    elif args.action == "delete":
        MANAGER.del_person(args.name)


def task(args: Tap, manager: Manager):
    if args.action == "add":
        MANAGER.add_task(args.name)
    elif args.action == "delete":
        MANAGER.del_task(args.name)


class AssignmentSubparser(Tap):
    action: Literal["add", "delete"]
    person: str
    task: str

    def configure(self):
        self.set_defaults(func=assign)


class PersonSubparser(Tap):
    action: Literal["add", "delete"]
    name: str

    def configure(self):
        self.set_defaults(func=person)


class TaskSubparser(Tap):
    action: Literal["add", "delete"]
    name: str

    def configure(self):
        self.set_defaults(func=task)


class SimpleArgumentParser(Tap):
    def configure(self):
        self.add_subparsers(help="sub-command help")
        self.add_subparser("assign", AssignmentSubparser, help="assignment help")
        self.add_subparser("person", PersonSubparser, help="person help")
        self.add_subparser("task", TaskSubparser, help="task help")


if __name__ == "__main__":
    args = SimpleArgumentParser().parse_args()
    args.func(args)
