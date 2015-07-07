from __future__ import print_function
import os

import alias


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
