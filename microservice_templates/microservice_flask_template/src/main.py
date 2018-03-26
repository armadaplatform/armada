from collections import Counter
import json
import os
import random
import requests
from armada import hermes

from flask import Flask, Response
from raven.contrib.flask import Sentry

config = hermes.get_config('config.json', {})

app = Flask(__name__)

sentry = Sentry(app, dsn=config.get('sentry_url'))

rums = Counter()

@app.route('/')
def status():
    return "OK"


@app.route('/drink/<user>/<int:count>', methods=['POST'])
def drink(user, count):

    rums_limit = config.get('rums_limit', 1)
    if int(count) > rums_limit:
        return "You can't drink that much! The limit is {0}.\n".format(rums_limit)

    rums[user] += int(count)
    return "{0}'s rums count is now {1}.\n".format(user, rums[user])


@app.route('/report')
def report():
    r = Response(response=json.dumps(rums, sort_keys=True, indent=4) + "\n", status=200)
    r.headers["Content-Type"] = "application/json"
    return r


@app.route('/delay/<int:seconds>')
def delay(seconds):
    session = requests.Session()
    result = session.get('http://httpbin.org/delay/{0}?rnd={1}'.format(seconds, random.random()))
    r = Response(response=result.text + "\n", status=200)
    r.headers["Content-Type"] = "application/json"
    return r
