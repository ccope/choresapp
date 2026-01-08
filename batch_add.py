from dotenv import load_dotenv

from chores.manager import Manager


load_dotenv()
people = {
    "Cam": "chores@camcope.me",
    "Evie": "evie.friday@gmail.com",
    "Nicole": "nglabinski@gmail.com",
}

tasks = {
    "bathroom": "Clean the hall bathroom- mirror, sink, counter, toilet, shower floor, vacuum, trash",
    "compost": "Take out the compost.",
    "swiffering": "Swiffer visible spots in dining room, all of kitchen",
    "pickup day": "Take down all the stuff and put the bins on the curb",
    "recycling": "Take out the recycling.",
    "stove": "Clean stove grilles and surface.",
    "surfaces": "Wipe down countertops, dining table, coffee table, microwave, toaster",
    "trash": "Take out the trash.",
    "vacuum": "Vacuum floors in kitchen+living/dining room+hallway",  # UPDATE DESCRIPTION
}


schedule_data = {
    "bathroom": "monthly",
    "compost": "nag",
    "swiffering": "biweekly after roomba-ing",
    "pickup day": "wednesday morning",
    "recycling": "nag",
    "stove": "biweekly nag",
    "surfaces": "biweekly",
    "trash": "nag",
    "vacuum": "sunday+thursday",
}

assignments = {
    "bathroom": ["Cam", "Evie"],
    "compost": ["Cam", "Evie", "Nicole"],
    "recycling": ["Cam", "Evie", "Nicole"],
    "stove": ["Cam", "Evie", "Nicole"],
    "surfaces": ["Cam", "Evie", "Nicole"],
    "trash": ["Cam", "Evie", "Nicole"],
    "vacuum": ["Cam", "Evie", "Nicole"],
}

MANAGER = Manager()

for person, email in people.items():
    MANAGER.add_person(person, email)

for task, peeps in assignments.items():
    MANAGER.add_task(task, tasks[task])
    for person in peeps:
        MANAGER.assign_task(person, task)
