import os
import random
from datetime import datetime
from email.message import Message
from textwrap import dedent
from typing import Any, Dict, List

from flask import Flask, Request, render_template, request
from flask_sqlalchemy_session import current_session
from sqlalchemy.sql import select, and_
from sqlalchemy.orm import selectinload

from chores.lib import get_assignees_sorted_by_count
from chores.models.choresdb import Assignments, People, Tasks

template_dir = os.path.abspath("templates")
fmt = "%a, %d %b %Y %H:%M:%S %z"
app = Flask(__name__, template_folder=template_dir)


# TODO: Think about renaming... everything
def validate_web_form(form: Dict[str, str], fields: List[str]) -> Dict[str, Any]:
    ret = {}
    map_form_to_db = {"name": "person", "chore": "task"}
    for field in fields:
        form_value = form[field]
        obj = None
        if field == "chore":
            obj = (
                current_session.execute(select(Tasks).where(Tasks.name == form_value))
                .scalars()
                .one()
            )

        if field == "name":
            obj = (
                current_session.execute(select(People).where(People.name == form_value))
                .scalars()
                .one()
            )
        if obj:
            ret[map_form_to_db[field]] = obj
        else:
            raise KeyError("Unknown field!")
    if ret.get("person") and ret.get("task"):
        a_st = select(Assignments).where(
            and_(
                Assignments.people_id == ret["person"].id,
                Assignments.task_id == ret["task"].id,
            )
        )
        try:
            assignment = current_session.execute(a_st).scalars().one()
            ret["assignment"] = assignment
        except Exception:
            raise ValueError("That person doesn't have to do that chore, dawg.")
    return ret


class ProxiedRequest(Request):
    def __init__(self, environ, populate_request=True, shallow=False):
        super(Request, self).__init__(environ, populate_request, shallow)
        # Support SSL termination. Mutate the host_url within Flask to use https://
        # if the SSL was terminated.
        x_forwarded_proto = self.headers.get("X-Forwarded-Proto")
        if x_forwarded_proto == "https":
            self.url = self.url.replace("http://", "https://")
            self.host_url = self.host_url.replace("http://", "https://")
            self.base_url = self.base_url.replace("http://", "https://")
            self.url_root = self.url_root.replace("http://", "https://")


app.request_class = ProxiedRequest


@app.route("/")
def displaychores():
    tasks = current_session.execute(select(Tasks.name)).scalars()
    names = current_session.execute(select(People.name)).scalars()
    return render_template("chores.html", chores=list(tasks), names=list(names))


@app.route("/nag", methods=["POST"])
def nag():
    try:
        data = validate_web_form(request.form, ["chore"])
    except KeyError:
        raise ValueError("Bad form, SNOZZBALL.")
    task_obj = data["task"]
    assignees = get_assignees_sorted_by_count(current_session, task_obj)
    person_obj = assignees[0].person
    emails = [p.person.email for p in assignees[1:]]
    msg = Message()
    subject = "%s NEEDS TO DO THE %s" % (person_obj.name, task_obj.name)
    msg.set_payload(task_obj.description)
    msg["Subject"] = subject
    msg["Date"] = datetime.now().strftime(fmt)
    msg["From"] = "Chore Master <address@todo.fixme>"
    msg["To"] = person_obj.email
    msg["Cc"] = emails
    msg["Reply-To"] = ""
    msg.preamble = "\n"
    app.config["notifyer"].send(msg)
    return dedent(
        """
        <!doctype html>
        <html>
        <head></head>
        <body>
        %s has been nagged to %s.
        <script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script>
        </body>
        </html>"""
        % (person_obj.name, task_obj.name, request.url_root)
    )


@app.route("/done", methods=["POST"])
def done():
    try:
        data = validate_web_form(request.form, ["name", "chore"])
    except ValueError as e:
        return e.msg
    person_obj = data["person"]
    task_obj = data["task"]
    assignment: Assignments = data["assignment"]
    assignment.counter += 1
    current_session.commit()
    emails = [p.person.email for p in task_obj.people if p.person.email != person_obj.email]
    msg = Message()
    msg["Subject"] = "%s %sed. Thanks!" % (person_obj.name, task_obj.name)
    msg["Date"] = datetime.now().strftime(fmt)
    msg["From"] = "Chore Master <address@todo.fixme>"
    msg["To"] = person_obj.email
    msg["Cc"] = emails
    msg["Reply-To"] = ""
    msg.preamble = "\n"
    try:
        app.config["notifyer"].send(msg)
    except Exception as e:
        print("failed to email: %s" % e)
        return "failed to email %s!" % person_obj.name
    return dedent(
        """
        <!doctype html>
        <html>
        <head></head>
        <body>
        Thanks.
        <script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script>
        </body>
        </html>"""
        % request.url_root
    )
