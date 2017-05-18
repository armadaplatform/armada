from __future__ import print_function

import os
from datetime import datetime

import requests
from requests.exceptions import SSLError
from urlparse import urlparse

from armada_command import armada_api
from armada_command.dockyard import alias
from armada_command.scripts.compat import json


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


def get_dockyard_alias(image_name, is_run_locally):
    if is_run_locally and image_name == os.environ.get('MICROSERVICE_NAME'):
        return 'local'
    return get_default_alias()


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


CA_FILE_WILDCARDS = [
    '/etc/docker/certs.d/{}/ca.crt',
    '/usr/local/share/ca-certificates/{}.crt',
    '/etc/pki/ca-trust/source/anchors/{}.crt',
]


def _get_ca_file_path(domain):
    for wildcard in CA_FILE_WILDCARDS:
        file_path = wildcard.format(domain)
        if os.path.exists(file_path):
            return file_path
    return None


def _http_get(url, **kwargs):
    parsed_url = urlparse(url)
    verify_tls = True
    if parsed_url.scheme == 'https':
        domain = parsed_url.netloc
        ca_file_path = _get_ca_file_path(domain)
        if ca_file_path:
            verify_tls = ca_file_path
    return requests.get(url, verify=verify_tls, **kwargs)


DOCKYARD_API_ENDPOINTS = {
    'v1': '/_ping',
    'v2': '/v2',
}


class DockyardDetectionException(Exception):
    def __init__(self, reason, specific_reason=None):
        self.specific_reason = specific_reason
        self.reason = '{}: {}'.format(reason, specific_reason or 'Is it a dockyard?')
        super(DockyardDetectionException, self).__init__(self.reason)

    def is_specific(self):
        return self.specific_reason is not None


def detect_dockyard_api_version(dockyard_address, user, password):
    possible_reason = None
    for api_version, endpoint in DOCKYARD_API_ENDPOINTS.items():
        try:
            url = dockyard_address.rstrip('/') + endpoint
            auth = None
            if user and password:
                auth = (user, password)
            try:
                r = _http_get(url, timeout=2, auth=auth)
                if r.status_code == requests.codes.unauthorized:
                    possible_reason = 'Unauthorized request. HTTP code: {}'.format(r.status_code)
                if r.status_code == requests.codes.ok and r.text == '{}':
                    return api_version
            except SSLError as e:
                possible_reason = 'SSLError: {}'.format(e)
        except:
            pass
    raise DockyardDetectionException('Could not detect dockyard API version', possible_reason)


class DockyardFactoryException(Exception):
    pass


def remote_dockyard_factory(url, user=None, password=None):
    if bool(user) != bool(password):
        raise DockyardFactoryException('user and password have to be both present, or both absent.')
    auth = (user, password) if user and password else None

    parsed_url = urlparse(url)
    protocol = parsed_url.scheme
    api_version = None
    most_specific_exception = None
    if not protocol:
        if auth:
            protocol = 'https'
        else:
            try:
                api_version = detect_dockyard_api_version('https://' + url, user, password)
                protocol = 'https'
            except DockyardDetectionException as e:
                protocol = 'http'
                if e.is_specific():
                    most_specific_exception = e
        url = '{}://{}'.format(protocol, url)
    if api_version is None:
        try:
            api_version = detect_dockyard_api_version(url, user, password)
        except DockyardDetectionException as e:
            if most_specific_exception is None or e.is_specific():
                most_specific_exception = e
            raise most_specific_exception

    if api_version == 'v1':
        return DockyardV1(url, auth)
    if api_version == 'v2':
        return DockyardV2(url, auth)
    raise DockyardFactoryException('Unknown dockyard API version: {}'.format(api_version))


def dockyard_factory(url, user=None, password=None):
    if not url:
        return LocalDockyard()
    return remote_dockyard_factory(url, user, password)


class Dockyard(object):
    url = None

    def __init__(self):
        pass

    def get_image_creation_time(self, name, tag='latest'):
        raise NotImplementedError()

    def is_remote(self):
        raise NotImplementedError()

    def is_http(self):
        return NotImplementedError()


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

    def get_image_creation_time(self, name, tag='latest'):
        url = '{}/v2/{}/manifests/{}'.format(self.url, name, tag)
        manifests = _http_get(url, auth=self.auth).json()
        if 'history' not in manifests:
            return None
        return max([json.loads(history['v1Compatibility'])['created'] for history in manifests['history']])


class LocalDockyard(Dockyard):
    def __init__(self):
        super(LocalDockyard, self).__init__()

    def get_image_creation_time(self, name, tag='latest'):
        images_response = json.loads(armada_api.get('images/{}'.format(name)))
        if images_response['status'] == 'ok':
            image_infos = json.loads(images_response['image_info'])
            name_with_tag = '{}:{}'.format(name, tag)
            image_info_for_tag = [image_info for image_info in image_infos if name_with_tag in image_info['RepoTags']]
            if image_info_for_tag:
                return datetime.utcfromtimestamp(int(image_info_for_tag[0]['Created'])).isoformat()
        return None

    def is_remote(self):
        return False
