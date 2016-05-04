from __future__ import print_function

import json
import os
import sys
import traceback

import web
from armada_backend.api_create import Create
from armada_backend.api_start import Start

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

class Run(Create, Start):
    LENGTH_OF_SHORT_CONTAINER_ID = 12

    def POST(self):
        try:
            post_data = json.loads(web.data())
        except:
            traceback.print_exc()
            return self.status_error('API Run: Invalid input JSON.')

        try:
            short_container_id, service_endpoints = self._run_service(post_data)
            return self.status_ok({'container_id': short_container_id, 'endpoints': service_endpoints})
        except Exception as e:
            traceback.print_exc()
            return self.status_exception("Cannot run service", e)

    def _run_service(self, run_parameters):
        long_container_id = self._create_service(**run_parameters)
        short_container_id = long_container_id[:self.LENGTH_OF_SHORT_CONTAINER_ID]
        service_endpoints = self._start_container(long_container_id)
        return short_container_id, service_endpoints







