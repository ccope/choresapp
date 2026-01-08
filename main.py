#!/usr/bin/env python
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from flask_sqlalchemy_session import flask_scoped_session

from chores.autonag import AutoNag
from chores.notification_service import get_notification_provider
from chores.web import app


load_dotenv()
engine = create_engine(os.environ["DBURI"], connect_args={"check_same_thread": False}, future=True)
SessionFactory = sessionmaker(autoflush=False, bind=engine)
flask_scoped_session(SessionFactory, app)
notification_provider_name = os.environ.get("NOTIFICATIONS")
notification_provider = get_notification_provider(notification_provider_name)
app.config["notifyer"] = notification_provider
schedule = None
#with Session(engine) as session:
#    res = session.execute(text("select * from schedule"))
#autonag = AutoNag(engine, notification_provider)
#autonag.start()
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=9001)
else:
    application = app
