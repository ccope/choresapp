#!/usr/bin/env python
import os

from dotenv import load_dotenv
from flask_migrate import Migrate

from chores.notification_service import get_notification_provider
from chores.web import app
from chores.models.choresdb import db


load_dotenv()
notification_provider_name = os.environ.get("NOTIFICATIONS")
notification_provider = get_notification_provider(notification_provider_name)
app.config["notifyer"] = notification_provider
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DBURI"]
db.init_app(app)
Migrate(app, db, render_as_batch=True)
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=9001)
