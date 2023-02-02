import random
from typing import List
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload

from chores.models.choresdb import Assignments, People, Tasks


def get_assignees_sorted_by_count(session, task_obj: Tasks) -> List[People]:
    assigned_people = (
        session.execute(
            select(Assignments)
            .options(selectinload(Assignments.person))
            .where(Assignments.task_id == task_obj.id)
            .order_by(Assignments.counter.asc())
        )
        .scalars()
        .all()
    )
    # If this is a fresh task, ensure the order is random
    # all tasks may be fresh so the same person could get pinged every time
    if assigned_people[0].counter == 0:
        zeros = []
        for a in assigned_people:
            if a.counter == 0:
                zeros.append(a)
        rand = random.choice(zeros)
        person_obj = rand.person
    else:
        person_obj = assigned_people[0].person
    the_rest = [p.person for p in assigned_people if not p.people_id == person_obj.id]
    return [person_obj] + the_rest
