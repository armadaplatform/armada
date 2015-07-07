import json
import datetime

import requests

from armada_command import armada_api
from armada_command.armada_utils import ArmadaCommandException
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import is_dockyard_address_accessible

class ArmadaImage(object):
    def __init__(self, microservice_name_or_image_path, dockyard_alias=None):
        self.dockyard_address, self.microservice_name = ArmadaImage.__split_image_path(microservice_name_or_image_path)
        self.dockyard_alias = dockyard_alias
        self.dockyard_dict = None
        self.dockyard_auth = None
        self.dockyard_url = None
        if self.dockyard_address:
            if dockyard_alias:
                raise ArmadaCommandException('Ambiguous dockyard. Please specify either -d/--dockyard '
                                             'or dockyard_ip[:port]/microservice_name')
            self.image_path = microservice_name_or_image_path
        elif dockyard_alias == 'local':
            self.image_path = microservice_name_or_image_path
        else:
            self.dockyard_dict = dockyard.get_dockyard_dict(self.dockyard_alias)
            self.dockyard_address = self.dockyard_dict['address']
            self.image_path = self.dockyard_address + '/' + self.microservice_name
        if self.dockyard_address:
            if self.dockyard_dict and 'user' in self.dockyard_dict and 'password' in self.dockyard_dict:
                self.dockyard_auth = (self.dockyard_dict['user'], self.dockyard_dict['password'])

            if '://' in self.dockyard_address:
                self.dockyard_url = self.dockyard_address
            else:
                if self.dockyard_auth or is_dockyard_address_accessible("https://" + self.dockyard_address):
                    protocol = 'https'
                else:
                    protocol = 'http'
                self.dockyard_url = protocol + '://' + self.dockyard_address

    def is_remote(self):
        return self.dockyard_address is not None

    def __str__(self):
        return self.image_path

    def __get_local_image_creation_time(self):
        images_response = json.loads(armada_api.get('images/{self.microservice_name}'.format(**locals())))
        if images_response['status'] == 'ok':
            image_info = json.loads(images_response['image_info'])
            if image_info:
                return datetime.datetime.utcfromtimestamp(int(image_info[0]['Created'])).isoformat()
            else:
                return None

    def __get_remote_long_image_id(self):
        url = '{self.dockyard_url}/v1/repositories/{self.microservice_name}/tags/latest'.format(**locals())
        response = requests.get(url, auth=self.dockyard_auth)
        if response.status_code != requests.codes.ok:
            raise ArmadaCommandException('HTTP error ({response.status_code}) on url: {url}'.format(**locals()))
        return json.loads(response.text)

    def __get_remote_image_creation_time(self):
        long_image_id = self.__get_remote_long_image_id()
        url = '{self.dockyard_url}/v1/images/{long_image_id}/json'.format(**locals())
        response = requests.get(url, auth=self.dockyard_auth)
        if response.status_code != requests.codes.ok:
            raise ArmadaCommandException('HTTP error ({response.status_code}) on url: {url}'.format(**locals()))
        image_dict = json.loads(response.text)
        if image_dict and 'created' in image_dict:
            return image_dict['created']
        else:
            return None

    def get_image_creation_time(self):
        try:
            if self.is_remote():
                return self.__get_remote_image_creation_time()
            else:
                return self.__get_local_image_creation_time()
        except:
            return None

    def exists(self):
        try:
            return self.get_image_creation_time() is not None
        except:
            return False

    @staticmethod
    def __split_image_path(image_path):
        if '/' in image_path:
            return image_path.split('/', 1)
        return None, image_path


def select_latest_image(*armada_images):
    return max((armada_image for armada_image in armada_images), key=lambda i: i.get_image_creation_time() if i else '')
