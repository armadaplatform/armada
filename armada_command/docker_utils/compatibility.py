from __future__ import print_function

import argparse
import os
import re
import shutil
import sys
from distutils.version import StrictVersion
from subprocess import check_call, check_output, CalledProcessError
from tempfile import mkdtemp

DOCKER_STATIC_CLIENT_DIR = '/opt/armada-docker-client/'


def _get_docker_version():
    output = check_output(['docker', '--version'])
    match = re.search(r'^Docker version (?P<version>\d+\.\d+\.\d+)', output)
    try:
        return match.group('version')
    except AttributeError:
        raise Exception("Couldn't determine docker version.")


def _get_subclasses(base_class):
    for cls in base_class.__subclasses__():
        yield cls
        for subcls in _get_subclasses(cls):
            yield subcls


def _docker_backend_factory():
    version = StrictVerboseVersion(_get_docker_version())
    for subclass in set(_get_subclasses(BaseDockerBackend)):
        if subclass.is_supported_version(version):
            return subclass(version)
    print("Docker version {} is unsupported.".format(version), file=sys.stderr)
    sys.exit(1)


class StrictVerboseVersion(StrictVersion):
    def __str__(self):
        vstring = '.'.join(map(str, self.version))
        if self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])
        return vstring


class DockerBackendMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        attrs['versions_range'] = map(mcs.wrap_with_strict_version, attrs['versions_range'])
        return type.__new__(mcs, name, bases, attrs)

    @staticmethod
    def wrap_with_strict_version(vstring):
        if vstring is not None:
            try:
                return StrictVerboseVersion(vstring)
            except ValueError:
                raise Exception('Invalid version number.')
        return vstring


class BaseDockerBackend(object):
    # <min_ver, max_ver)
    versions_range = (None, None)
    __metaclass__ = DockerBackendMetaclass

    def __init__(self, current_version):
        self.current_version = current_version

    @classmethod
    def is_supported_version(cls, version):
        min_ver, max_ver = cls.versions_range
        if all(cls.versions_range):
            return min_ver <= version < max_ver
        if min_ver is None:
            raise Exception('{} is improperly configured, at least minimal version should be provided'
                            .format(cls.__name__))
        return min_ver <= version

    def get_static_docker_client(self):
        raise NotImplementedError


class DockerBackendV1(BaseDockerBackend):
    versions_range = ('1.12.0', '17.03.0')

    def get_static_docker_client(self):
        self._get_static_docker_client(str(self.current_version))

    def _get_static_docker_client(self, version_string):
        if not os.path.isdir(DOCKER_STATIC_CLIENT_DIR):
            os.mkdir(DOCKER_STATIC_CLIENT_DIR)

        cached_version_name = 'docker-{}'.format(version_string)
        cached_version_path = os.path.join(DOCKER_STATIC_CLIENT_DIR, cached_version_name)
        if not os.path.isfile(cached_version_path):
            print("Fetching static docker client v{}.".format(version_string))
            url = 'https://get.docker.com/builds/Linux/x86_64/{}'.format(cached_version_name)
            self._download_static_docker_client(url, cached_version_path)

    @staticmethod
    def _download_static_docker_client(url, output_file):
        url = '{}.tgz'.format(url)
        tmp_dir = mkdtemp()
        tmp_compressed_file = os.path.join(tmp_dir, 'docker.tgz')
        try:
            check_call(['curl', '-sSL', url, '-o', tmp_compressed_file])
            check_call(['tar', '-xzf', tmp_compressed_file, '-C', tmp_dir])
            check_call(['mv', os.path.join(tmp_dir, 'docker/docker'), output_file])
            check_call(['chmod', '+x', output_file])
        except CalledProcessError as e:
            print("An error occurred while trying to download docker's client: {}".format(e), file=sys.stderr)
        finally:
            shutil.rmtree(tmp_dir)


class DockerBackendV2(DockerBackendV1):
    versions_range = ('17.03.0', None)

    def get_static_docker_client(self):
        ce_version_string = '{}.{:02}.{}-ce'.format(*self.current_version.version)
        self._get_static_docker_client(ce_version_string)


docker_backend = _docker_backend_factory()


def get_static_docker_client(args):
    docker_backend.get_static_docker_client()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers()

    cache_parser = sub_parser.add_parser('cache-client')
    cache_parser.set_defaults(func=get_static_docker_client)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print('Error: {}'.format(e))
        sys.exit(1)
