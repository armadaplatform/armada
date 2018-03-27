import sys
import os

microservice_name = os.environ.get('MICROSERVICE_NAME', 'microservice_flask')

sys.path.insert(0, '/opt/{0}/src/'.format(microservice_name))
from main import app as application
