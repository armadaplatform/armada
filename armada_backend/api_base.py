import json

import web

from utils import get_logger


def _create_response_with_error(error_msg=None):
    return json.dumps({'status': 'error', 'error': error_msg or ''})


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

    def status_error(self, message=None):
        get_logger().error('API error: {}'.format(message))
        return _create_response_with_error(message)

    def status_exception(self, message, exception):
        get_logger().exception(exception)
        error_msg = "{0}. {1} - {2}".format(message,
                                            type(exception).__name__,
                                            str(exception))
        return _create_response_with_error(error_msg)

    def status_ok(self, extra_result=None):
        extra_result = extra_result or {}
        extra_result['status'] = 'ok'
        return json.dumps(extra_result)
