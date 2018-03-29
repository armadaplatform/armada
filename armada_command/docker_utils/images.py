from abc import ABCMeta

from armada_command.armada_utils import split_image_path
from armada_command.dockyard import dockyard
from armada_command.dockyard.alias import DOCKYARD_FALLBACK_ADDRESS


class InvalidImagePathException(Exception):
    pass


class ArmadaImageFactory(object):
    def __new__(cls, image_path, dockyard_alias=None, fallback_service_name=None):
        dockyard_address, image_name, image_tag = split_image_path(image_path)
        image_name = image_name or fallback_service_name

        if not image_name:
            raise InvalidImagePathException

        if not dockyard_address and not dockyard_alias and image_name.startswith('microservice'):
            dockyard_address = DOCKYARD_FALLBACK_ADDRESS

        if dockyard_alias == 'local':
            return LocalArmadaImage(dockyard_address, image_name, image_tag)

        if dockyard_alias and dockyard_address:
            dockyard_address = None

        return RemoteArmadaImage(dockyard_address, image_name, image_tag, dockyard_alias)


class ArmadaImage(object):
    __metaclass__ = ABCMeta

    def __init__(self, dockyard_address, image_name, image_tag):
        super(ArmadaImage, self).__init__()
        self.dockyard_address = dockyard_address
        self.image_name = image_name
        self.image_tag = image_tag
        self.image_path = '{}/{}'.format(dockyard_address, image_name) if dockyard_address else image_name
        self._dockyard = None

    @property
    def image_name_with_tag(self):
        if self.image_tag:
            return '{}:{}'.format(self.image_name, self.image_tag)
        return self.image_name

    @property
    def image_path_with_tag(self):
        if self.image_tag:
            return '{}:{}'.format(self.image_path, self.image_tag)
        return self.image_path

    def is_remote(self):
        raise NotImplementedError

    def __str__(self):
        return self.image_path

    def get_image_creation_time(self):
        return self.dockyard.get_image_creation_time(self.image_path, self.image_tag)

    def exists(self):
        return self.get_image_creation_time() is not None

    @property
    def dockyard(self):
        raise NotImplementedError


class LocalArmadaImage(ArmadaImage):
    def __init__(self, dockyard_address, image_name, image_tag='latest'):
        super(LocalArmadaImage, self).__init__(dockyard_address, image_name, image_tag)

    @property
    def dockyard(self):
        if self._dockyard is None:
            self._dockyard = dockyard.LocalDockyard()
        return self._dockyard

    def is_remote(self):
        return False


class RemoteArmadaImage(ArmadaImage):
    def __init__(self, dockyard_address, image_name, image_tag, dockyard_alias):
        self._dockyard_dict = {}
        if not dockyard_address:
            self._dockyard_dict = dockyard.get_dockyard_dict(dockyard_alias)
            dockyard_address = self._dockyard_dict['address']
        self.dockyard_alias = dockyard_alias
        super(RemoteArmadaImage, self).__init__(dockyard_address, image_name, image_tag)

    @property
    def dockyard(self):
        if self._dockyard is None:
            dockyard_address = self.dockyard_address
            if not dockyard_address:
                self._dockyard_dict = dockyard.get_dockyard_dict(self.dockyard_alias)
                dockyard_address = self._dockyard_dict['address']
            self._dockyard = dockyard.remote_dockyard_factory(dockyard_address,
                                                              self._dockyard_dict.get('user'),
                                                              self._dockyard_dict.get('password'))
        return self._dockyard

    def is_remote(self):
        return True


def select_latest_image(*armada_images):
    return max((armada_image for armada_image in armada_images), key=lambda i: i.get_image_creation_time() if i else '')
