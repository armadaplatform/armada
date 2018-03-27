# microservice-flask

This is a base microservice image for Armada services written using [Flask](http://flask.pocoo.org/) python framework.


# Idea

Main intent of this base image is to provide ability to run Flask app in concurrent way, e.g. in production environment.
This is achieved by running it under apache2 + mod_wsgi.

Single threaded developer's environment may also be configured.


# Example

We'll build example flask app [example-rum-counter](./example-rum-counter/) based on `coffee-counter` example
from Armada documentation. It has endpoint `/delay/{n}` which we can use to simulate long running request
that takes `n` seconds to complete.

    armada build microservice_flask
    cd ./example-rum-counter
    armada build example-rum-counter -d local

    # Run in development mode.
    armada run example-rum-counter -d local -p 1129:80 --env dev
    for i in `seq 7`; do curl http://localhost:1129/delay/5 2>&1 | grep rnd= & done
    # ^ The results will be received one by one every 5 seconds.

    # Run in production mode (under apache2 with max. 4 concurrent requests).
    armada run example-rum-counter -d local -p 2911:80 --env production
    for i in `seq 11`; do curl http://localhost:2911/delay/5 2>&1 | grep rnd= & done
    # ^ The results will be received in batches of 4 proving that they were run in concurrent fashion.


# Configuration

`microservice_flask` reads its configuration by hermes from file `config.json`.
Following variables are supported:

- `use_apache` (`false`/`true`, default: `false`)

    Whether to run the application under apache2+mod_wsgi or as a standalone flask application.
    The latter is recommended during development. That mode has variable `FLASK_DEBUG` set to allow live reload
    of the application code. You can then edit code & instantly refresh much like in PHP development model.

- `apache_config` (dictionary)

    Dictionary of Apache variables that will be included in web server config.
    Following variables are taken into account by `microservice_flask` itself:

    - `wsgi_worker_threads_count` (default: 17)

    Number of concurrent requests that can be served by the service at any one time.


# Flask app development

`microservice_flask` looks for application to run in the folder `/opt/{MICROSERVICE_NAME}/src/`,
where `{MICROSERVICE_NAME}` is the value of the environment variable.
Thus, so far, the base image doesn't support container renaming, and the name of the service should match
the name of its image.
The main app file has to called `main.py`.


# Other

The requests to Flask app are not timed-out by Apache, so there is a risk that all worker threads will hang
and the service will become unresponsive. Few of the possible solutions to this situation:

* Move to Ubuntu 16.10 and install python 3.6 with newer libapache2-mod-wsgi-py3.
Then we could use `request-timeout` configuration option in `WSGIDaemonProcess`.

* Write simple watchdog script, that will restart apache2 as soon as some health-check request takes longer
than previously set threshold.

* Use nginx instead of apache2.
