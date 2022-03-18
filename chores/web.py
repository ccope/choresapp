import os
from datetime import datetime
from email.message import Message

from flask import Flask, render_template, request, g
from sqlalchemy.sql import select


template_dir = os.path.abspath('templates')
fmt = '%a, %d %b %Y %H:%M:%S %z'
app = Flask(__name__, template_folder=template_dir)


@app.route('/')
def displaychores():
    stmt = select(Tasks)
    tasks = g.conn.execute(stmt)
    chores = []
    names = []
    for id, name, description, people in chores:
        chores.append(name)
        names.append([x.name for x in people])
    return render_template('chores.html', chores=chores, names=names)


@app.route('/nag', methods=["POST"])
def nag():
    chore = request.form['chore']
    chores = g.conn.execute()
    if chore not in [c.name for c in chores]:
        return "Invalid chore, loser."
    doer = g.conn.execute(select(Assignments).order_by(Assignments.c.counter, desc()))
    #doer = config["order"][0]
    for name in config["order"]:
        if status[chore][doer] > status[chore][name]:
            doer = name
    msg = Message()
    subject = ''
    if chore in config["descriptions"]:
        subject = "%s NEEDS TO DO THE %s" % (doer, chore)
        msg.set_payload(config["descriptions"][chore])
    else:
        subject = "%s NEEDS TO DO THE %s (eom)" % (doer, chore)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime(fmt)
    msg['From'] = "Chore Master <address@todo.fixme>"
    msg['To'] = config["emails"][doer]
    msg['Cc'] = config["emails"].values() - msg['To']
    msg['Reply-To'] = ""
    msg.preamble = "\n"
    g.email.send(msg)
    return """<!doctype html>
<html><head></head><body>%s has been nagged to %s.<script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script></body></html>""" % (doer, chore, request.url_root)


@app.route('/done', methods=["POST"])
def done():
    chore = request.form['chore']
    if chore not in status:
        return "Invalid chore, COMMIE."
    try:
        if request.form['name'] not in config["order"]:
            return "Invalid person, dickhead."
    except KeyError:
        return "Bad form, SNOZZBALL."
    status[chore][request.form['name']] += 1
    with open('chores.json', 'w') as choresjson:
        json.dump(status, choresjson)
    msg = Message()
    msg['Subject'] = "%s %sed. Thanks. (eom)" % (request.form['name'], chore)
    msg['Date'] = datetime.now().strftime(fmt)
    msg['From'] = "Chore Master <address@todo.fixme>"
    msg['To'] = status["emails"][request.form['name']]
    msg['Cc'] = ""  # TODO change before release
    msg['Reply-To'] = ""
    msg.preamble = "\n"
    try:
        g.email.send(msg)
    except Exception as e:
        print("failed to email: %s" % e)
    return """<!doctype html>
<html><head></head><body>Thanks.<script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script></body></html>""" % request.url_root


