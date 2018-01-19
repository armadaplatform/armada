from armada_backend.utils import get_logger


def _create_response_with_error(error_msg=None):
    return {'status': 'error', 'error': error_msg or ''}


class ApiCommand(object):
    def get_get_parameter(self, req, parameter_name):
        try:
            get_data = req.get_parameter(parameter_name)
            result = get_data[parameter_name]
        except:
            return None, "Invalid input data - no parameter '{0}'.".format(parameter_name)
        return result, None

    def get_post_parameter(self, req, parameter_name):
        try:
            post_data = req.json
        except:
            return None, 'Invalid input data - invalid json.'

        try:
            result = post_data[parameter_name]
        except:
            return None, "Invalid input data - no parameter '{0}'.".format(parameter_name)

        return result, None

    def status_error(self, resp, message=None):
        get_logger().error('API error: %s', message)
        resp.json = _create_response_with_error(message)

    def status_exception(self, resp, message, exception):
        get_logger().exception(exception)
        error_msg = "API exception: {0}. {1} - {2}".format(message, type(exception).__name__, str(exception))
        resp.json = _create_response_with_error(error_msg)

    def status_ok(self, resp, extra_result=None):
        extra_result = extra_result or {}
        extra_result['status'] = 'ok'
        resp.json = extra_result
