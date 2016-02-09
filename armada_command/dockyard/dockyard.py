from __future__ import print_function

import json
import os
from datetime import datetime
from pprint import pprint
from urlparse import urlparse

import requests

import alias
from armada_command import armada_api


class DockyardException(Exception):
    pass


class CriticalDockyardException(Exception):
    pass


def get_default_alias():
    default_alias = alias.get_default()
    if default_alias:
        dockyard = alias.get_alias(default_alias)
        if not dockyard:
            raise DockyardException('Default dockyard does not exist.')
        return default_alias
    alias_list = alias.get_list()
    if not alias_list:
        raise DockyardException('There are no running dockyards.')
    if len(alias_list) > 1:
        raise CriticalDockyardException('There are multiple running dockyards and no default set.'
                                        'Please specify dockyard by -d/--dockyard or set the default.')
    return alias_list[0]['name']


def get_dockyard_alias(microservice_name, is_run_locally):
    if is_run_locally and microservice_name == os.environ.get('MICROSERVICE_NAME'):
        return 'local'
    if '/' not in microservice_name:
        return get_default_alias()
    return None


def get_dockyard_dict(alias_name=None):
    try:
        if not alias_name:
            alias_name = get_default_alias()
        dockyard = alias.get_alias(alias_name)
        if not dockyard:
            raise CriticalDockyardException('Dockyard alias: {alias_name} does not exist.'.format(**locals()))
        return dockyard
    except DockyardException as e:
        dockyard_address = alias.DOCKYARD_FALLBACK_ADDRESS
        print('WARNING: Could not get dockyard_address ({e}), falling back to: {dockyard_address}'.format(**locals()))
        return {'address': dockyard_address}


def get_dockyard_address(alias_name=None):
    return get_dockyard_dict(alias_name)['address']


DOCKYARD_API_ENDPOINTS = {
    'v1': '_ping',
    'v2': 'v2',
}


def _get_ca_file_path(domain):
    ca_file_path = '/usr/local/share/ca-certificates/{}.crt'.format(domain)
    if os.path.exists(ca_file_path):
        return ca_file_path
    return None


def _http_get(url, **kwargs):
    parsed_url = urlparse(url)
    verify_tls = True
    if parsed_url.scheme == 'https':
        domain = parsed_url.netloc
        ca_file_path = _get_ca_file_path(domain)
        if ca_file_path:
            verify_tls = ca_file_path
    print(url, verify_tls, kwargs)
    return requests.get(url, verify=verify_tls, **kwargs)


def detect_dockyard_api_version(dockyard_address, user, password):
    for api_version, endpoint in DOCKYARD_API_ENDPOINTS.items():
        try:
            url = dockyard_address.rstrip('/') + '/' + endpoint
            auth = None
            # verify_tls = True
            if user and password:
                auth = (user, password)
            # else:
            #     verify_tls = False

            # r = requests.get(url, timeout=2, auth=auth, verify=verify_tls)
            print('http_get: {} {}'.format(url, auth))
            r = _http_get(url, timeout=2, auth=auth)
            print(r)
            if r.status_code == requests.codes.ok and r.text == '{}':
                return api_version
        except:
            pass
    return None


class DockyardFactoryException(Exception):
    pass


def dockyard_factory(url, user=None, password=None):
    if not url:
        return LocalDockyard()

    if bool(user) != bool(password):
        raise DockyardFactoryException('user and password have to be both present, or both absent.')
    auth = (user, password) if user and password else None

    parsed_url = urlparse(url)
    protocol = parsed_url.scheme
    api_version = None
    if not protocol:
        if auth:
            protocol = 'https'
        else:
            api_version = detect_dockyard_api_version('https://' + url, user, password)
            print('detection1: {}'.format(api_version))
            if api_version is not None:
                protocol = 'https'
            else:
                protocol = 'http'
        url = '{}://{}'.format(protocol, url)
    if api_version is None:
        api_version = detect_dockyard_api_version(url, user, password)
        print('detection2: {}'.format(api_version))
    if api_version is None:
        raise DockyardFactoryException('Could not detect dockyard API version. Is it a dockyard?')
    if api_version == 'v1':
        return DockyardV1(url, auth)
    if api_version == 'v2':
        return DockyardV2(url, auth)
    raise DockyardFactoryException('Unknown dockyard API version: {}'.format(api_version))


class Dockyard(object):
    def __init__(self):
        pass

    def get_image_creation_time(self, image_name, tag='latest'):
        raise NotImplementedError()

    def is_remote(self):
        raise NotImplementedError


class RemoteDockyard(Dockyard):
    def __init__(self, url, auth=None):
        super(Dockyard, self).__init__()
        self.url = url
        self.auth = auth

    def is_remote(self):
        return True

    def is_http(self):
        return urlparse(self.url).scheme == 'http'


class DockyardV1(RemoteDockyard):
    def __init__(self, url, auth=None):
        super(DockyardV1, self).__init__(url, auth)

    def get_image_creation_time(self, name, tag='latest'):
        long_image_id = self.__get_remote_long_image_id(name, tag)
        url = '{}/v1/images/{}/json'.format(self.url, long_image_id)
        image_dict = _http_get(url, auth=self.auth).json()
        return str(image_dict.get('created'))

    def __get_remote_long_image_id(self, name, tag='latest'):
        url = '{}/v1/repositories/{}/tags/{}'.format(self.url, name, tag)
        return _http_get(url, auth=self.auth).json()


class DockyardV2(RemoteDockyard):
    def __init__(self, url, auth=None):
        super(DockyardV2, self).__init__(url, auth)

    def get_image_creation_time(self, image_name, tag='latest'):
        url = '{}/v2/{}/manifests/{}'.format(self.url, image_name, tag)
        manifests = _http_get(url, auth=self.auth).json()
        # pprint(manifests)
        if 'history' not in manifests:
            return None
        return max([json.loads(history['v1Compatibility'])['created'] for history in manifests['history']])


class LocalDockyard(Dockyard):
    def __init__(self):
        super(LocalDockyard, self).__init__()

    def get_image_creation_time(self, image_name, tag='latest'):
        images_response = json.loads(armada_api.get('images/{}:{}'.format(image_name, tag)))
        if images_response['status'] == 'ok':
            image_info = json.loads(images_response['image_info'])
            if image_info:
                return datetime.utcfromtimestamp(int(image_info[0]['Created'])).isoformat()
        return None

    def is_remote(self):
        return False


if __name__ == '__main__':
    d1 = DockyardV1('http://dockyard.armada.sh')
    pprint(d1.get_image_creation_time('example'))

    # d2 = DockyardV2('https://dockyard-v2.dev')
    d2 = DockyardV2('https://dockyard.fi')
    pprint(d2.get_image_creation_time('example-python'))

    dl = LocalDockyard()
    pprint(dl.get_image_creation_time('example-python'))
