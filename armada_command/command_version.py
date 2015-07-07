import argparse
import requests
from armada_command.consul.consul import consul_query


def parse_args():
    parser = argparse.ArgumentParser(description="Display armada version.")
    return parser.parse_args()


def add_arguments(parser):
    pass


def command_version(args):
    version = "none"
    agent_services_dict = consul_query('agent/services')
    for service in agent_services_dict.values():
        if service['Service'] == 'armada':
            port = service['Port']
            url = "http://localhost:{port}/version".format(**locals())
            result = requests.get(url)
            try:
                version = result.text
            except AttributeError:
                version = "error"
            break
    print(version)
