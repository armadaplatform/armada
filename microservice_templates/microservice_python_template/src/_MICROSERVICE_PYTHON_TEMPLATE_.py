import web


class Index(object):
    def GET(self):
        return 'Service works!'


def main():
    urls = (
        '/', Index.__name__,
    )
    app = web.application(urls, globals())
    app.run()


if __name__ == '__main__':
    main()
