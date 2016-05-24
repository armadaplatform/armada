from bottle import route, run


@route('/')
def index():
    return 'Service works!'


run(host='0.0.0.0', port=80)
