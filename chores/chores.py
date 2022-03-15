#!/usr/bin/env python

import json
import os
from datetime import datetime
from email.message import Message
from typing import Optional

from flask import Flask, render_template, request

from chores.email import EmailProvider

with open('data/chores.json') as choresjson:
    status = json.load(choresjson)

template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)
fmt = '%a, %d %b %Y %H:%M:%S %z'

def get_email_provider(name: Optional[str]) -> EmailProvider:
    if name == "AWS":
        from chores.email.aws import SesEmail
        return SesEmail()
    elif name == "Google":
        from chores.email.gmail import GMailEmail
        return GMailEmail()
    raise Exception("Invalid email provider!")

@app.route('/')
def displaychores():
    chores = []
    names = status["order"]
    for k in status:
        if k not in ["order", "emails", "descriptions"]:
            chores.append(k)
    return render_template('chores.html', chores=chores, names=names)

@app.route('/nag', methods=["POST"])
def nag():
    chore = request.form['chore']
    if chore in ["order", "emails", "descriptions"] or chore not in status:
        return "Invalid chore, loser."
    doer = status["order"][0]
    for name in status["order"]:
        if status[chore][doer] > status[chore][name]:
            doer = name
    msg = Message()
    subject = ''
    if chore in status["descriptions"]:
        subject = "%s NEEDS TO DO THE %s" % (doer, chore)
        msg.set_payload(status["descriptions"][chore])
    else:
        subject = "%s NEEDS TO DO THE %s (eom)" % (doer, chore)
    msg['Subject'] = subject
    msg['Date'] = datetime.now().strftime(fmt)
    msg['From'] = "Chore Master <address@todo.fixme>"
    msg['To'] = status["emails"][doer]
    msg['Cc'] = "" # TODO change before release
    msg['Reply-To'] = ""
    msg.preamble = "\n"
    g.email.send(msg)
    return """<!doctype html>
<html><head></head><body>%s has been nagged to %s.<script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script></body></html>""" % (doer, chore, request.url_root)

@app.route('/done', methods=["POST"])
def done():
    chore = request.form['chore']
    if chore in ["order", "emails", "descriptions"] or chore not in status:
        return "Invalid chore, COMMIE."
    try:
        if request.form['name'] not in status["order"]:
            return "Invalid person, dickhead."
    except KeyError:
        return "Bad form, SNOZZBALL."
    status[chore][request.form['name']] += 1
    with open('chores.json', 'w') as choresjson:
        json.dump(status, choresjson)
    msg = Message()
    msg['Subject'] = "%s %sed. Thanks. (eom)" % (request.form['name'], chore)
    msg['Date'] = datetime.now().strftime(fmt)
    msg['From'] = "Hodgepodge Chore Master <address@todo.fixme>"
    msg['To'] = status["emails"][request.form['name']]
    msg['Cc'] = "" # TODO change before release
    msg['Reply-To'] = ""
    msg.preamble = "\n"
    try:
        g.email.send(msg)
    except Exception as e:
        print("failed to email: %s" % e)
    return """<!doctype html>
<html><head></head><body>Thanks.<script>setTimeout(function() { window.location.assign("%s"); }, 2500);</script></body></html>""" % request.url_root

if __name__ == '__main__':
    email_provider_name = os.environ.get("EMAIL_PROVIDER")
    with get_email_provider(email_provider_name) as email_provider:
        g.email = email_provider
    app.run(debug=False, host='0.0.0.0', port=9001)
