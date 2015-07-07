import web


class Health(object):
    def GET(self):
        return 'ok'


def main():
    urls = (
        '/health', Health.__name__,
    )
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
