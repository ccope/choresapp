import random
from typing import List
from sqlalchemy.sql import select
from sqlalchemy.orm import selectinload

from chores.models.choresdb import Assignments, People, Tasks


def get_assignment_leaderboard(session, task_obj: Tasks) -> List[Assignments]:
    return session.execute(
            select(Assignments)
            .options(selectinload(Assignments.person))
            .where(Assignments.task_id == task_obj.id)
            .order_by(Assignments.counter.asc())
            ).scalars().all()

def get_assignees_sorted_by_count(session, task_obj: Tasks) -> List[People]:
    assignments = get_assignment_leaderboard(session, task_obj)
    if len(assignments) == 0:
        return []
    # If this is a fresh task, ensure the order is random
    # all tasks may be fresh so the same person could get pinged every time
    if assignments[0].counter == 0:
        zeros: List[Assignments] = []
        for a in assignments:
            if a.counter == 0:
                zeros.append(a)
            else:
                break
        if len(zeros) > 1:
            random.shuffle(zeros)
            assignments = zeros + assignments[len(zeros):]

    return [p.person for p in assignments]
