from armada_backend import api_base


class Register(api_base.ApiCommand):
    def POST(self):
        try:
            result = {}
        except Exception as e:
            return self.status_exception('Could not get armada info.', e)
        return self.status_ok({'result': result})
