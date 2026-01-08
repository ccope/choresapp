from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.schedulers.sync import Scheduler

from chores.lib import get_assignees_sorted_by_count


class AutoNag:
    def __init__(self, engine, notifier):
        datastore = SQLAlchemyDataStore(engine)
        self.scheduler = Scheduler(data_store=datastore)
        self.notifier = notifier

    def myjob(self):
        pycord = "do something"

    def setup_schedules(self):
        self.scheduler.add_job(self.myjob, 'calendarinterval', weeks=2, hour=8, minute=0)

    def start(self):
        self.setup_schedules()
        self.scheduler.start_in_background()
