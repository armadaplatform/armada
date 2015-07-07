import json
import web

class ApiCommand(object):

    def get_get_parameter(self, parameter_name):
        try:
            get_data = web.input()
            result = get_data[parameter_name]
        except:
            return None, "Invalid input data - no parameter '{0}'.".format(parameter_name)
        return result, None


    def get_post_parameter(self, parameter_name):
        try:
            post_data = json.loads(web.data())
        except:
            return None, 'Invalid input data - invalid json.'

        try:
            result = post_data[parameter_name]
        except:
            return None, "Invalid input data - no parameter '{0}'.".format(parameter_name)

        return result, None


    def status_error(self, message = None):
        return json.dumps({'status': 'error', 'error': message or ''})


    def status_ok(self, extra_result = {}):
        extra_result['status'] = 'ok'
        return json.dumps(extra_result)
