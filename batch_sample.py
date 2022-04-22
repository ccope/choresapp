import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from admin import g, add_person, add_task, assign_task


load_dotenv()
assignments = {"task1": ["person1", "person2"], "task2": ["person1"]}

people = {"person1": "person1@email.address", "person2": "person2@email.address"}

tasks = {"task1": "task1 description.", "task2": "task2 description"}

g["engine"] = create_engine(os.environ["DBURI"], future=True)

for person, email in people.items():
    add_person(person, email)

for task, peeps in assignments.items():
    add_task(task, tasks[task])
    for person in peeps:
        assign_task(person, task)
