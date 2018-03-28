from armada import hermes

import logging
from flask import Flask

from raven.contrib.flask import Sentry

config = hermes.get_config('config.json', {})

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

logging.getLogger('werkzeug').handlers = []
logging.getLogger('werkzeug').addHandler(handler)

app = Flask(__name__)

sentry = Sentry(app, dsn=config.get('sentry_url'))

@app.route('/')
def status():
    return "OKej"

