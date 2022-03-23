import os
from datetime import datetime
from email.message import Message
from textwrap import dedent
from typing import Dict, Tuple

from flask import Flask, render_template, request
from flask_sqlalchemy_session import current_session
from sqlalchemy.sql import select, and_
from sqlalchemy.orm import selectinload

from chores.models.choresdb import Assignments, People, Tasks

template_dir = os.path.abspath('templates')
fmt = '%a, %d %b %Y %H:%M:%S %z'
app = Flask(__name__, template_folder=template_dir)


@app.route('/')
def displaychores():
    tasks = current_session.execute(select(Tasks.name)).scalars()
    names = current_session.execute(select(People.name)).scalars()
    return render_template('chores.html', chores=list(tasks), names=list(names))


@app.route('/nag', methods=["POST"])
def nag():
    try:
        task_name = request.form['chore']
    except KeyError:
        raise ValueError("Bad form, SNOZZBALL.")
    task_obj = current_session.execute(select(Tasks)
                                       .where(Tasks.name == task_name)
                                       ).scalars().one()
    assigned_people = current_session.execute(
            select(Assignments).options(selectinload(Assignments.person))
            .where(Assignments.task_id == task_obj.id)
            .order_by(Assignments.counter.asc())
            ).scalars().all()
    person_obj = assigned_people[0].person
    emails = [p.person.email for p in assigned_people[1:]]
    msg = Message()
    subject = "%s NEEDS TO DO THE %s" % (person_obj.name, task_name)
    msg.set_payload(task_obj.description)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime(fmt)
    msg['From'] = "Chore Master <address@todo.fixme>"
    msg['To'] = person_obj.email
    msg['Cc'] = emails
    msg['Reply-To'] = ""
    msg.preamble = "\n"
    app.config['email'].send(msg)
    return dedent("""
        <!doctype html>
        <html>
        <head></head>
        <body>
        %s has been nagged to %s.
        <script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script>
        </body>
        </html>""" % (person_obj.name, task_name, request.url_root))


def validate_web_form(form: Dict[str, str]) -> Tuple[People, Tasks]:
    try:
        person_name = form['name']
        task_name = form['chore']
    except KeyError:
        raise ValueError("Bad form, SNOZZBALL.")
    task_obj = current_session.execute(
                   select(Tasks)
                   .where(Tasks.name == task_name)
                   ).scalars().one()
    person_obj = current_session.execute(
                     select(People)
                     .where(People.name == person_name)
                     ).scalars().one()
    if not task_obj:
        raise ValueError("Invalid chore, COMMIE.")
    if not person_obj:
        raise ValueError("Invalid person, dickhead.")
    a_st = select(Assignments).where(
            and_(Assignments.people_id == person_obj.id,
                 Assignments.task_id == task_obj.id))
    try:
        assignment = current_session.execute(a_st).scalars().one()
    except Exception:
        raise ValueError("That person doesn't have to do that chore, dawg.")
    return person_obj, task_obj


@app.route('/done', methods=["POST"])
def done():
    try:
        person_obj, task_obj = validate_web_form(request.form)
    except ValueError as e:
        return e.msg
    print(task_obj.people)
    emails = [p.person.email for p in task_obj.people if p.person.email != person_obj.email]
    print(emails)
    msg = Message()
    msg['Subject'] = "%s %sed. Thanks. (eom)" % (person_obj.name, task_obj.name)
    msg['Date'] = datetime.now().strftime(fmt)
    msg['From'] = "Chore Master <address@todo.fixme>"
    msg['To'] = person_obj.email
    msg['Cc'] = emails
    msg['Reply-To'] = ""
    msg.preamble = "\n"
    try:
        app.config['email'].send(msg)
    except Exception as e:
        print("failed to email: %s" % e)
        return "failed to email %s!" % person_obj.name
    return dedent("""
        <!doctype html>
        <html>
        <head></head>
        <body>
        Thanks.
        <script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script>
        </body>
        </html>""" % request.url_root)
