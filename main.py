#!/usr/bin/env python
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session

from chores.email_service import get_email_provider
#from chores.models.choresdb import Assignments, People, Tasks, Timers
from chores.web import app


DBURI = "sqlite+pysqlite:///chores.db"
engine = create_engine(DBURI, connect_args={"check_same_thread": False},
                       echo=True, future=True)
SessionFactory = sessionmaker(autoflush=False, bind=engine)
flask_scoped_session(SessionFactory, app)
email_provider_name = os.environ.get("EMAIL_PROVIDER")
email_provider = get_email_provider(email_provider_name)
app.config['email'] = email_provider
app.run(debug=False, host='0.0.0.0', port=9001)
