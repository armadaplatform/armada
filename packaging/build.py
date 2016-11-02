from argparse import ArgumentParser
import logging
import os
import shutil
import subprocess
from os import path
from tempfile import mkdtemp

defaults = {
    'name': 'armada',
    'home_path': '/opt/armada',
    'docker_compatibility_src': 'armada_command/docker_utils/compatibility.py',
    'docker_compatibility_path': '/opt/armada/docker_compatibility.py',
    'autocomplete_src': 'packaging/bash_completion.d/armada',
    'autocomplete_path': '/etc/bash_completion.d/armada',

    'binaries_path': '/usr/local/bin/',
    'binaries': ['armada', 'armada-runner'],
    'binaries_src': 'packaging/bin',

    'default_file_src': 'packaging/default/armada',
    'default_file_path': '/etc/default/armada',

    'initd_script_src': 'packaging/init.d/armada',
    'initd_script_file_path': '/etc/init.d/armada',

    'systemd_file_src': 'packaging/systemd/armada.service',
    'systemd_service_file_path': '/etc/systemd/system/armada.service',
    'postinst_src': 'packaging/install.sh',

}


def get_logger():
    logger = logging.getLogger('armada_packaging')
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


logger = get_logger()


def main():
    ap = ArgumentParser()
    ap.add_argument('--version')
    args = ap.parse_args()
    version = args.version

    _cleanup_dist()
    create_deb_package(version)
    create_rpm_package(version)
    create_amazon_linux_package(version)

    logger.info('All packages creates successfully and stored in dist folder.')


def create_deb_package(version):
    deb = {
        'package_type': 'deb',
        'depends': ['python', 'python-pip', 'conntrack'],
    }
    packaging_options = defaults.copy()
    packaging_options.update(deb)
    logger.info('Creating deb package')
    _create_package(packaging_options, version)


def create_rpm_package(version):
    rpm = {
        'package_type': 'rpm',
        'depends': ['python', 'python-pip', 'conntrack-tools', 'net-tools'],
    }
    packaging_options = defaults.copy()
    packaging_options.update(rpm)
    logger.info('Creating rpm package')
    _create_package(packaging_options, version)


def create_amazon_linux_package(version):
    # amazon linux has custom installed pip, and default python in version 2.6.x
    rpm = {
        'package_type': 'rpm',
        'depends': ['conntrack-tools', 'net-tools'],
        'name': 'armada-amzn',
    }
    packaging_options = defaults.copy()
    packaging_options.update(rpm)
    logger.info('Creating amazon linux package')
    _create_package(packaging_options, version)


def _create_env(options, version):
    tmp_dir = mkdtemp(prefix='armada_package')
    _create_package_dirs(options, tmp_dir)

    for bin in options['binaries']:
        dest = _path_join(tmp_dir, options['binaries_path'], bin)
        shutil.copy2(_path_join(options['binaries_src'], bin), dest)
        os.chmod(dest, 0o755)

    shutil.copy2(_path_join(options['docker_compatibility_src']),
                 _path_join(tmp_dir, options['docker_compatibility_path']))
    shutil.copy2(_path_join(options['autocomplete_src']),
                 _path_join(tmp_dir, options['autocomplete_path']))
    shutil.copy2(_path_join(options['default_file_src']), _path_join(tmp_dir, options['default_file_path']))
    shutil.copy2(_path_join(options['initd_script_src']), _path_join(tmp_dir, options['initd_script_file_path']))
    shutil.copy2(_path_join(options['systemd_file_src']), _path_join(tmp_dir, options['systemd_service_file_path']))

    with open(_path_join(tmp_dir, '/opt/armada', 'version'), 'wt') as f:
        f.write('ARMADA_VERSION={}'.format(version))

    return tmp_dir


def _cleanup_dist():
    shutil.rmtree('./dist', ignore_errors=True)
    os.mkdir('./dist')


def _path_join(*args):
    # if os.path.join detect that component is an absolute path, it thrown away previous ones
    return path.normpath('/'.join(args))


def _create_package_dirs(options, tmp_dir):
    for key, value in options.items():
        if not isinstance(key, str) or not key.endswith('path'):
            continue
        base_dir = path.dirname(value)
        os.makedirs(_path_join(tmp_dir, base_dir), exist_ok=True)


def _create_package(options, version):
    packege_root = _create_env(defaults, version)

    fpm_options = [
        "fpm",
        "-t", options['package_type'],
        "-s", "dir",
        "--description", "armada",
        "-C", packege_root,
        "--license", "\"Apache 2.0\"",
        "--maintainer", "cerebro@ganymede.eu",
        "--url", "armada.sh",
        "--config-files", options['default_file_path'],
        "--after-install", options['postinst_src'],
        "--name", options['name'],
        "--version", version,
        "--architecture", 'x86_64',
        "-p", "./dist",

    ]
    for dep in options['depends']:
        fpm_options += ['--depends', dep]
    try:
        subprocess.check_output(fpm_options)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
        raise


if __name__ == '__main__':
    main()
