from dotenv import load_dotenv

from chores.manager import Manager

load_dotenv()

MANAGER = Manager()

assignments = {"task1": ["person1", "person2"], "task2": ["person1"]}

people = {"person1": "person1@email.address", "person2": "person2@email.address"}

tasks = {"task1": "task1 description.", "task2": "task2 description"}

for person, email in people.items():
    MANAGER.add_person(person, email)

for task, peeps in assignments.items():
    MANAGER.add_task(task, tasks[task])
    for person in peeps:
        MANAGER.assign_task(person, task)
