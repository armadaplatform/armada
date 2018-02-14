from armada_command import armada_api


def command_version(args):
    version = armada_api.get('version')
    print(version)
