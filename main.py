#!/usr/bin/env python
import os

from sqlalchemy import create_engine
from flask import g

from chores.email_service import get_email_provider
from chores.models.choresdb import Assignments, People, Tasks, Timers
from chores.web import app


if __name__ == '__main__':
    email_provider_name = os.environ.get("EMAIL_PROVIDER")
    email_provider = get_email_provider(email_provider_name)
    g.email = email_provider
    engine = create_engine("sqlite+pysqlite:///chores.db", echo=True, future=True)
    with engine.connect() as conn:
        g.db = conn
    app.run(debug=False, host='0.0.0.0', port=9001)
