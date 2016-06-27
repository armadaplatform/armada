from armada_command.armada_utils import ArmadaCommandException, split_image_path
from armada_command.dockyard import dockyard


class InvalidImagePathException(Exception):
    pass


class ArmadaImageFactory(object):
    def __new__(cls, image_path, dockyard_alias=None, fallback_service_name=None):
        dockyard_address, image_name, image_tag = split_image_path(image_path)
        image_name = image_name or fallback_service_name

        if not image_name:
            raise InvalidImagePathException

        if dockyard_alias == 'local':
            return LocalArmadaImage(dockyard_address, image_name, image_tag)

        if dockyard_alias and dockyard_address:
            raise ArmadaCommandException('Ambiguous dockyard. Please specify either -d/--dockyard '
                                         'or dockyard_hostname[:port]/image_name')

        return RemoteArmadaImage(dockyard_address, image_name, image_tag, dockyard_alias)


class LocalArmadaImage(object):
    def __init__(self, dockyard_address, image_name, image_tag):
        self.image_tag = image_tag
        self.image_name = image_name
        self.dockyard_address = dockyard_address
        self.dockyard = dockyard.LocalDockyard()

        image_path = image_name
        if dockyard_address:
            image_path = '{}/{}'.format(dockyard_address, image_path)
        self.image_path = image_path

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
        return self.dockyard.is_remote()

    def __str__(self):
        return self.image_path

    def get_image_creation_time(self):
        return self.dockyard.get_image_creation_time(self.image_name, self.image_tag)

    def exists(self):
        return self.get_image_creation_time() is not None


class RemoteArmadaImage(LocalArmadaImage):
    def __init__(self, dockyard_address, image_name, image_tag, dockyard_alias):
        self.image_name, self.image_tag = image_name, image_tag
        dockyard_dict = {}
        if not dockyard_address:
            dockyard_dict = dockyard.get_dockyard_dict(dockyard_alias)
            dockyard_address = dockyard_dict['address']

        self.image_path = '{}/{}'.format(dockyard_address, self.image_name)
        self.dockyard = dockyard.remote_dockyard_factory(dockyard_address,
                                                         dockyard_dict.get('user'),
                                                         dockyard_dict.get('password'))


def select_latest_image(*armada_images):
    return max((armada_image for armada_image in armada_images), key=lambda i: i.get_image_creation_time() if i else '')
