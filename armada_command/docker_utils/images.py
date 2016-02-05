from armada_command.armada_utils import ArmadaCommandException
from armada_command.dockyard import dockyard
from armada_command.dockyard.dockyard import dockyard_factory


class ArmadaImage(object):
    def __init__(self, image_path, dockyard_alias=None):
        self.dockyard_alias = dockyard_alias
        self.dockyard_dict = None
        self.dockyard_auth = None
        self.dockyard_url = None
        self.dockyard = None
        dockyard_address, self.image_name = ArmadaImage.__split_image_path(image_path)
        if dockyard_address:
            if dockyard_alias:
                raise ArmadaCommandException('Ambiguous dockyard. Please specify either -d/--dockyard '
                                             'or dockyard_ip[:port]/microservice_name')
            self.image_path = image_path
        elif dockyard_alias == 'local':
            self.image_path = image_path
        else:
            self.dockyard_dict = dockyard.get_dockyard_dict(self.dockyard_alias)
            dockyard_address = self.dockyard_dict['address']
            self.image_path = dockyard_address + '/' + self.image_name

        self.dockyard = dockyard_factory(dockyard_address,
                                         self.dockyard_dict.get('user'),
                                         self.dockyard_dict.get('password'))

    def is_remote(self):
        return self.dockyard.is_remote()

    def __str__(self):
        return self.image_path

    def get_image_creation_time(self):
        return self.dockyard.get_image_creation_time(self.image_name)

    def exists(self):
        return self.get_image_creation_time() is not None

    @staticmethod
    def __split_image_path(image_path):
        if '/' in image_path:
            return image_path.split('/', 1)
        return None, image_path


def select_latest_image(*armada_images):
    return max((armada_image for armada_image in armada_images), key=lambda i: i.get_image_creation_time() if i else '')
