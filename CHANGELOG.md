# Changelog

# Changelog

## 2.13.1 (2025-05-27)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

- Updated Python dependencies to latest versions (colored, contextlib2, docker, falcon, paramiko, requests, urllib3, ujson, uwsgi)
- Added support for Ubuntu Noble (24.04) microservice base images
- Modified Docker client and API integration for compatibility with updated docker library
- Enhanced ship management and version API functionality
- Updated development commands and utilities
- Improved gitignore configuration

## 2.11.43 (2025-03-06)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.41 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.37 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.31 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.23 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.19 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.17 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.13 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.
- Fixed builder image

## 2.11.11 (2025-02-18)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.
- Fixed colored package version

## 2.11.7 (2025-02-17)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.
- Fixed microservice_focal image

## 2.11.6 (2025-02-17)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## 2.11.5 (2025-02-17)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.
- Added --ssh option to the build command in Armada, allowing SSH keys to be forwarded into the container during build.
- Fixed microservice_packaging image

## 2.11.4 (2025-02-17)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

### Improvements
- A set of new `microservice_node...` base images added, including:
    -  `microservice_node16` (based on `microservice`).
    -  `microservice_node14_focal` (based on `microservice_focal`).
    -  `microservice_node16_focal` (based on `microservice_focal`).

## 2.11.3 (2021-03-10)

We do best effort to support docker versions 1.12.0 - 20.10.4 with this release.

## Bug fixes
- Fixed `armada ssh` command for docker >= 19.03.14.

## 2.11.2 (2021-03-02)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

## Bug fixes
* Fixed `armada diagnose` command for `microservice_focal` images on older armada versions
    by adding alias `python` --> `python3` in those images.

## 2.11.1 (2021-02-11)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

## Bug fixes
- Fix armada installation for docker >= 18.09.0.
- Fix pip locale problems during armada installation.

## 2.11.0 (2021-02-02)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Improvements
- A new `microservice_focal` (ubuntu20.04) base image added. It's version bumped to `2.11.0`.
- A new `microservice_python3_focal` base image added (based on `microservice_focal`).
- Armada built on top of the `microservice_python3_focal` base image. It's version bumped to `2.11.0`.
- Armada commands migrated to python3. Python2 dependency dropped.
- `Haproxy` version upgraded from `1.8` to `2.2`.
- Dropping support for Amazon Linux 1.
- RPM package of Armada works fine with Amazon Linux 2.

### Bug fixes
* Fix broken dependency (Falcon Json Middleware) for backend.
* Allow binding armada to interfaces with more than one IP address.

## 2.10.0 (2019-01-31)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.
### Improvements
- Python3 version in base image `microservice_python3` has been upgraded from `python3.6` to `python3.7`.
- Don't build deprecated `microservice_python3.5`.
- Armada internal API is now running on `python3.7`.
- By default don't show logs from garbage collector in `microservice_node*`

## 2.9.1 (2018-11-02)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Bug fixes
- Fix microservice image not starting.

## 2.9.0 (2018-10-31)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Features
- Add `nodejs` `v10.x`, remove unsupported `v4.x` version.

### Bug fixes
- Fix generating `CONFIG_PATH` on renamed microservices.

## 2.8.1 (2018-05-09)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Bug fixes
-Fix stopping/recovering services saved to KV-store using ship IP instead of name.

## 2.8.0 (2018-04-24)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Features
- Added new microservice_flask base image
- Added flask template


## 2.7.1 (2018-03-29)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Bug fixes
- Fix pushing images to remote dockyards with passwords.


## 2.7.0 (2018-03-21)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Features
- `armada build` supports multi-staged Dockerfiles.
- Base images in `armada build` may, and should now use explicit dockyard/docker registry addresses,
    e.g.: `FROM docker.io/golang:1.7.3`, or `FROM dockyard.armada.sh/microservice`.

### Improvements
- Set `TimeoutStartSec=30min` in systemd unit to prevent timeouts
- Decreased number of Consul queries executed during saving containers in KV store
- Save missing containers in KV store
- If initial recovery is not completed after 10 minutes since armada start, armada has status `warning`

### Bug fixes
- Fix netcat version on ArchLinux
- Fix filtering crashed services by name

## 2.6.0 (2018-03-09)

We do best effort to support docker versions 1.12.0 - 17.12.1 with this release.

### Features
- Build tar.xz (pacman) linux package.

### Bug fixes
- Fix stopping armada service, caused ship lefts cluster
- Fix getting docker version in docker > 17.10

## 2.5.1 (2018-02-12)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Improvements
- Increase uwsgi timeout (aka harakiri) from 11s to 31s.
- Set uwsgi socket-timeout to 31s.
- Use 3 threads per uwsgi process instead of 2.
- Don't run http worker as separate process in uwsgi.
- Microservice image is now building from deb package.
- More verbose logs.

### Bug fixes
- Split unit tests for command (python 2) and backend (python 3).
- Fix bug with updating microservice_version in `armada list` for microservices with subservices.


## 2.5.0 (2018-02-05)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Features
- New API endpoint `/v1/local/ports/{microservice_id}` for microservices, available inside the container.
    - It returns the mapping of local ports in container to external ports on host. E.g:
    ```
    $ curl 172.17.0.1:8900/v1/local/ports/f30690a0f8af
    {"80/tcp": "4261/tcp"}
    ```
- New flag in `armada list`: `--microservice-version`. It shows the version of microservice package inside
    the container. Works only for microservices based on version >= 2.5.0.

### Improvements
- Armada internal API is now running on python3 + uwsgi + falcon.
- New internal API for microservices (registering service, reporting health checks).
    - It should not change behavior. This is only a step towards removing docker and consul dependencies
        in microservices.
- Upgrade `requests` pip package in `microservice` base image from 2.9.1 to 2.18.4.

## 2.4.3 (2018-01-11)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Improvements
- Bump `python3` to `3.6.4` in `microservice_python3`
- Python scripts in `microservice` base image are now a proper python package, and provide command `microservice`.
    - This is the new suggested way of calling microservice scripts:
        - `microservice require` instead of `python require_service.py`
        - `microservice register` instead of `python register_in_service_discovery.py`
- Upgrade haproxy in `microservice` base image from 1.7 to 1.8.
- Remove unused address_adapter in microservice base image.

### Bug fixes
- Fix setting empty flags in `require_service.py`/`microservice require`, i.e. `--app_id=""` and `--env=""`.


## 2.4.2 (2018-01-02)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Improvements
- local-magellan, in microservice base image, besides of configuring haproxy dumps mapping of local port -> IP:port to `/var/opt/service_to_addresses.json`.
E.g.
```
root@c1823ea048c5:/# cat /var/opt/service_to_addresses.json
{
    "2000": [
        "192.168.3.19:32822", 
        "192.168.3.19:32821"
    ]
}
```

## 2.4.1 (2017-12-01)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Improvements
- Improve sorting in armada list for services with subservices 

## 2.4.0 (2017-11-17)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Features
- Add useful bash functions `atail`, `acd`, `actl` - use `ahelp` for more informations.

## 2.3.0 (2017-11-03)

We do best effort to support docker versions 1.12.0 - 17.10.0 with this release.

### Features
- Add `IMAGE_NAME` environmental variable.
- Compatibility with new docker binary location for versions 17.03 - 17.10. It makes remote `armada ssh/diagnose`
    work again in those docker versions.
- Set default value of `CONFIG_DIR` to 'config', in `microservice` base image. Hermes will automatically search
    for configs in 'config' directory in your service.
- New command `alogs` available in `microservice` base image. It opens up midnight commander with supervisor logs on the
    left pane and service source on the right pane.
- Add bash completion for supervisorctl
- Add possibility to configure service requirements via hermes config. This allows us to require different services in different environments.
    In base microservice image required_service.py will try to find `service_discovery.json` in config path. More info in [docs](http://armada.sh/docs/advanced_features/service_discovery/)


### Improvements
- Get rid of ugly `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` warnings showing up in remote `armada ssh/diagnose`
    invocations, after restarting/upgrading armada.
- Get rid of ugly `bash: warning: setlocale: LC_ALL: cannot change locale (en_US.UTF-8)` warning in remote
    `armada ssh/diagnose` invocations.
- Clean up code responsible for support of services built on `microservice` image older than v0.11.0 (2015-12-07) in
    `armada diagnose`.

### Bug fixes
- Fix `build-armada` and `restart-armada` development scripts to work outside of armada development vagrant as well.
- Fix armada's health-check for validating if armada runtime settings have been restored, to work during development
    of armada.


## 2.2.0 (2017-10-19)

We do best effort to support docker versions 1.12.0 - 17.05.0 with this release.
### Features
- Add customization of `max_old_space_size` in base nodejs microservices by setting `MAX_OLD_SPACE_SIZE_MB` environmental variable.
    By default `MAX_OLD_SPACE_SIZE_MB`=256
- Add `vim` to `microservice`
- Set build-time variables using `--build-arg` flag.
- Build base nodejs microservices with currently supported `nodejs` version - v4, v6, v8 and v0.12.


### Improvements
- `armada develop` is now compatible with official `armada-vagrant` boxes.
- `armada stop` now supports stopping multiple services
- `armada list --quiet` returns only distinct container IDs
- `apache2` is running in the foreground in `microservice_php`, adding `logrotate` for log retention management.
- Use template for building base `nodejs` images.

### Bug fixes
- `armada stop` can remove remaining services from removed ship


## 2.1.2 (2017-09-20)

We do best effort to support docker versions 1.12.0 - 17.05.0 with this release.
### Bug fixes
- `HashiCorp Consul` downgraded to 0.7.5 version due to performance problems.
    
## 2.1.1 (2017-09-13)

We do best effort to support docker versions 1.12.0 - 17.05.0 with this release.

### Improvements

- `armada-runner` script now supports `ip` command instead `ifconfig` and `route`.
- `armada-runner` can easliy bind local network interface from now.
- `armada-runner` network interface autodetection when `$default_interface` in `/etc/default/armada` is empty or commented.
- `armada-runner` network interface can be set statically in `/etc/default/armada` and would not be changed even if not exists.
- Removed `net-tools` from dependecies of installation packages.
- `HashiCorp Consul` upgraded to 0.9.3 version.

## 2.1.0 (2017-07-25)

We do best effort to support docker versions 1.12.0 - 17.05.0 with this release.

### Features
- EXPERIMENTAL: `armada-heal` script, for healing overloaded armada ships, is available inside of the armada container.
    Use with caution. Details: https://github.com/armadaplatform/armada-heal

### Improvements
- Exponentially increasing periods between recover retries.
- Internal refactoring of storing services data in consul.
- Use only docker to build armada packages


## 2.0.0 (2017-07-10)

We do best effort to support docker versions 1.12.0 - 17.05.0 with this release.

### Breaking changes
- Dropped support for Docker <1.12.0

### Features
- Add hooks. Currently only `pre-stop` hook is available.
 Place your custom scripts under ./hooks/pre-stop/ directory to have them executed, when certain action occurs.
- New command `armada develop`. It sets up the environment for development of given service, i.e. MICROSERVICE_NAME,
    so that service's name is implied in other armada commands. By default it mounts current working directory to
    container, and assigns sticky port from range 4000..4999, based on hash of service name, that should be easy to
    memorize. Exporting `$MICROSERVICE_NAME` env variable is no longer recommended for development.

### Improvements
- Bump docker-py to 2.4.2

### Bug fixes
- `armada list --local` don't choose active instance among services registered with `--single-active-instance` flag. 
    This is to prevent unnecessary changes of active one between instances running on different ships.

## 1.17.0 (2017-06-20)

We do best effort to support docker versions 1.6.0 - 17.05.0 with this release.

### Features
- Compatibility with docker versions 1.13.0 - 17.05.0.

### Improvements
- `armada build --squash` uses `--squash` flag built into Docker (since 1.13), which is much faster and merges only the
    layers from currently built Dockerfile. To use it you need to turn on experimental flag in your Docker daemon:
    https://sreeninet.wordpress.com/2017/01/27/docker-1-13-experimental-features/

## 1.16.2 (2017-05-29)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fix `armada list` when one of ships has version < 1.6.0

## 1.16.1 (2017-05-24)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fix `armada list` when one of ships was renamed.

## 1.16.0 (2017-05-18)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- Add `DISTRIB_CODENAME`=xenial and `DISTRIB_RELEASE`=16.04 environmental variables.
- Add `less` and `sudo` to `microservice`

- You can now set retention for containers backups stored in `/opt/armada/saved_containers_backup/`. To do that, set
    `SAVED_CONTAINERS_BACKUP_RETENTION=N` variable (where `N` is integer with number of days stored) in
    `/etc/default/armada` on host.

### Improvements
- Don't install old `gcc` version in `microservice_python3`.
- Regular cleaning duplicated containers backup in `/opt/armada/saved_containers_backup/`.
- Optimize armada list.

### Bug fixes
- Fix autoreloading armada development version.
- Fix clearing sessions files in PHP Docker container.


## 1.15.1 (2017-05-12)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fix node version in `microservice_node` image based on Ubuntu 16.04.
- Add link to php config at `/etc/php5` in `microservice_php` for compatibility with pre Ubuntu 16.04 images.

## 1.15.0 (2017-05-08)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- Show "Env" and "AppID" as separate columns, instead of "Tags", in `armada list`.

### Improvements
- Cron clear sessions files in PHP Docker container.
- Use Ubuntu 16.04 instead of 14.04 as base in `microservice` image.
- Upgrade HAProxy from 1.6 to 1.7.

## 1.14.0 (2017-04-03)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Improvements
- Update consul from v0.6.4 to v0.7.5.

## 1.13.0 (2017-03-22)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- **[EXPERIMENTAL]** Stub of new command `armada deploy`. Currently this command is an alias for `armada restart -a`,
    however it accepts all arguments accepted by `armada run` command, as well as desired number of instances for given
    microservice. Eventually this command will be responsible for deploying new version of microservice: if it's already
    running then it will perform restart, otherwise it'll launch as many instances as needed to satisfy requirements.


## 1.12.2 (2017-03-01)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fix running `add-apt-repository` in `microservice_python3`.
- Fix building armada development version.

### Improvements
- Log exceptions in consul query.

## 1.12.1 (2017-02-21)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Improvements
- Log info about removed kv entries in armada cleaner.

## 1.12.0 (2017-02-06)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- Add flag `--single-active-instance` to `register_in_service_discovery.py` script. Services registered with this flag will
    have at most one available (status 'passing' or 'warning') instance in armada service discovery mechanisms. The
    other instances will receive status 'standby'.
- Add `-vv/--verbose` flag to all armada commands.
- `armada shutdown` now removes by default previously joined ships from `/opt/armada/runtime_settings.json`. Use
    `--keep-joined` flag for old behavior.

### Bug fixes
- Fix building pip packages in `microservice_python3`.
- Fixed cleaning crashed services on not promoted ships.
- Fix stop and restart of armada service on systemd.

## 1.11.0 (2017-01-13)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- Add `-vv/--verbose` flag to `armada create`.
- Base image for services created using DotNET Core 1.0
- Template for sample "Hello, world!" REST service.
- Base image `microservice_python3.5` is now **deprecated** in favor of upgraded `microservice_python3` with python3.6.

### Improvements
- Separated supervisor configs for `armada_agent` and `register_in_service_discovery` to make overriding the latter
    in services easier.
- Python3 version in base image `microservice_python3` has been upgraded from python3.4 to python3.6.

### Bug fixes
- Fixed bug where restarting service started without `env` was setting `MICROSERVICE_ENV` environment variable as `env`.

## 1.10.0 (2016-12-15)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- You can now point path to Dockerfile in `armada build` using `--file` flag (like `docker build`).

## 1.9.2 (2016-12-12)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fixed bug where not recovered containers stayed with `recovering` status.

## 1.9.1 (2016-11-29)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fixed restarting crashed services.

## 1.9.0 (2016-11-17)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- Build deb, rpm and amazon linux package.
- Privilege mode of docker containers can be specified in `/etc/default/armada`.

### Bug fixes
- Fix keeping stopped services in `crashed` state after `armada restart`.

## 1.8.2 (2016-11-14)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fixed stopping services in `started` state.

### Improvements
- Send request data to sentry, add tag ship_IP to events.

## 1.8.1 (2016-11-03)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fix getting services list when microservice_env is not set 

### Improvements
- Disable timeout in systemd service

## 1.8.0 (2016-10-31)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- Log errors to [sentry](https://github.com/getsentry/sentry). It can be enable by adding `sentry_url={url of project in sentry}` in `/etc/default/armada` config file.

### Bug fixes
- Armada builds from base image with proper tag. 

## 1.7.1 (2016-10-24)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Bug fixes
- Fixed bug in `/list` endpoint in clusters with old backups in K/V store

## 1.7.0 (2016-10-18)

We do best effort to support docker versions 1.6.0 - 1.12.1 with this release.

### Features
- New base image `microservice_node6` with node v6.

### Improvements
- Upgrade go in microservice_go base image from 1.5.3 to 1.6.3.
- Optimized `/list` endpoint
- Removed Consul watch `checks`
- Consul watch `keyprefix` narrowed down to local services
- Set locales to UTF-8 version

### Bug fixes
- Generating unique ID for services while recovering
- Fixed autoreloading armada backed in vagrant environment
- Fixed detecting stop of armada service in systemd
- Fixed recovering containers
- Removing services from Consul K/V store while armada shutdown

## 1.6.0 (2016-10-05)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Features
- Storing service restart parameters and status in K/V store.
- `armada recover` by default will try recover crashed services from K/V store

### Improvements
- Ship names survive joining armada
- Ship names must be unique
- `armada diagnose` properly prints last health-check for services based on old microservice image, along with deprecation warning. 


## 1.5.3 (2016-09-20)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Ensure services based on old `microservice` image do not register themselves back in Consul during `armada stop`.


## 1.5.2 (2016-09-09)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Fixed an issue with `armada ssh` ignoring `--local` flag.
- Fixed KeyError exception issue when connecting to remote service.

## 1.5.1 (2016-09-07)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Improvements
- `--env` parameter `armada run` by default take `MICROSERVICE_ENV` environment variable as value.

### Bug fixes
- Fixed restarting services which have been run using `MICROSERVICE_NAME` environment variable.

## 1.5.0 (2016-09-06)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Features
- Added flag `-s/--squash` to `armada build`. With this option armada try to minimize service image via docker-squash.

### Bug fixes
- Fixed an issue with `armada ssh` not accepting container ids.

### Improvements
- Merge `run_health_checks.py` and `register_in_service_discovery.py` into `armada_agent.py` in order to save resources, register_is_service_discovery.py is left for backward compatibility.
- Changed timeout in `armada stop` from 10s to 60s until SIGKILL is sent to container main process.


## 1.4.0 (2016-09-02)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Features
- Added service selection prompt to `armada ssh`. Whenever multiple matching services are found, user can easily select which instance they want to ssh into.
- Added `--no-prompt` flag to `armada ssh` which disables prompting mechanism and results in error if multiple matching services are found. 
- Added `-l/--local` flag to `armada ssh` which limits matched services to local machine.

### Improvements
- [Vagrant](https://github.com/armadaplatform/vagrant "Armada Vagrant") Use `socat` instead of `armada-bind` to proxy insecure dockyard connection through localhost.

### Bug fixes
- Properly deregister crashed sub-services. 
- Fixed a bug which caused `armada run` in development environment use 4999:80 port mapping, even if port 80 was explicitly overridden.


## 1.3.3 (2016-08-25)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Fixed armada service on `systemd` init system.

## 1.3.2 (2016-08-23)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Fixed critical bug with setting containers' config paths introduced in 1.3.0.


## 1.3.1 (2016-08-19)

### Bug fixes
- Fixed critical bug with mounting containers' volumes introduced in 1.3.0.


## 1.3.0 (2016-08-19)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Improvements
- Optionally restrict possible config directories. By default root directory is mounted inside armada container in read-only mode, to verify existence of `--config` paths.
This can be restricted by setting `RESTRICT_CUSTOM_CONFIG_DIRS` variable to a specific path. (e.g. /home/user/configs)

- `run` and `restart` commands can get IP address as '--ship' argument.

### Features
- `armada list` show services that should be running with additional statuses:
    - `recovering`
    - `not-recovered` if recovering was not successful 
    - `crashed` for not running containers
    - `armada stop` to remove service from list

    
### Bug fixes
- While default armada network interface is unavailable armada uses host default interface.
- Fixed logging of Armada CLI commands

## 1.2.2 (2016-08-04)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Fix `armada list` always assuming `-l/--local` flag.
- Revert old behavior in `armada list` that showed 'container_id' instead of 'microservice_id' in ID column.


## 1.2.1 (2016-08-04)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Fix filtering by `app_id` in `armada list`.
- Fix pyflakes issues.
- Fix installation of bash completion file.

## 1.2.0 (2016-08-03)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Features
- Added autocomplete of armada commands, dockyard aliases, services and ships names.

### Improvements
- 'armada list' command support wildcards *, ?.

### Bug fixes
- Remove HTTP_PROXY header.

## 1.1.1 (2016-07-19)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Bug fixes
- Fixed issue with unhandled exception during the installation process. 


## 1.1.0 (2016-07-19)

We do best effort to support docker versions 1.6.0 - 1.12.0 with this release.

### Features
- Added logging of Armada CLI
- Added support for docker 1.12.*

### Improvements
- After critical status of service health checks next check is run after 1s,2s,3s... until 10s or first pass of health checks.
- Enabled autoreload of Armada API in development Vagrant

## 1.0.0 (2016-07-08)

**Ahoy sailor!**  
**:tada: :birthday: Armada is celebrating one year anniversary! :birthday: :tada:**  
**Fair winds!**  
:anchor:  



We do best effort to support docker versions 1.6.0 - 1.10.3 with this release.

### Features
:balloon: Added indicator of current ship in 'armada info'.

### Bug fixes
:balloon: Fix log file permission error.  
:balloon: Fix getting docker pid on centos7.  
:balloon: Validate response from armada_api.get('version').  

### Improvements
:balloon: Install armada pip package (with hermes) in microservice_python* base images.


## 0.20.2 (2016-07-04)

We do best effort to support docker versions 1.6.0 - 1.10.3 with this release.

### Bug fixes
- Do not use local restart if --ship parameter is provided.
- Fix issue with fallback to the default dockyard alias if the -d options is not provided.

## 0.20.1 (2016-06-28)

We do best effort to support docker versions 1.6.0 - 1.10.3 with this release.

### Bug fixes
- Fix displaying the information about the new version.


## 0.20.0 (2016-06-28)

We do best effort to support docker versions 1.6.0 - 1.10.3 with this release.

### :warning: **UPGRADE WARNING** :warning:
Due to internal changes in Armada, all Armada agents within the same cluster need to be upgraded, otherwise
remote runs and restarts will not work, and `armada info` may contain incorrect names. Ships' names will have to be set once again using `armada name` command.

### Features
- Allow verbose output for `armada build` command.
- Added images versioning. Since now it's possible to build, push and run services using `service_name:tag` notation or `:tag` notation if the `MICROSERVICE_NAME` env is provided.
- Added warning about using outdated armada version. It can be disabled by adding the `check_updates=0` line to the `/etc/default/armada` config file.

### Improvements
- Upgrade Consul from version 0.6.3 to 0.6.4.
- Store names of Armada ships in Consul's kv store. `armada name` does not restart Armada service anymore and is much
faster.
- After joining Armada agent to cluster, Armada will detect running Couriers there and fetch configuration from them.

### Bug fixes
- Fix build of `microservice_python3.5` base image.


## 0.19.2 (2016-05-31)

### Improvements
- Retry after failure during stopping of Docker container.

### Bug fixes
- Fix bug with recovering multiple copies of the same service.
- Fix detection of Docker daemon start time, which could cause unnecessary recovery.
- Make sure python requests package is not updated in Armada service.
- Fix race condition in require_service.py, causing not registering service in local magellan.


## 0.19.1 (2016-05-25)

### Improvements
- Update haproxy in microservice image (used by local magellan), from 1.5 to 1.6.
- Increase timeout to docker api from 7s to 11s.

### Bug fixes
- Hold version of python requests package to 2.9.1 in microservice image.
- Fixed checking for newest local image of service on restart in vagrant development environment.
- Fix import errors in couple of backend scripts.


## 0.19.0 (2016-05-17)

### Improvements
- In vagrant for armada development (`Vagrantfile` in armada repository), the code used for armada CLI is now
mounted from local workstation.
- Moved armada installation script from [armada-website](https://github.com/armadaplatform/armada-website) repository to armada repository.
- Added OpenRC support (Contributed by [ryneeverett](https://github.com/ryneeverett)).

### Bug fixes
- Fixed issue with passing arguments to `armada ssh`.

## 0.18.0 (2016-05-09)

### Features
- Services can now be moved between ships in a cluster with `armada restart` command using `--ship` parameter.
- E.g.: `armada restart myservice --ship 10.0.0.2`
- If moved service contains mounted volumes or statically assigned ports, restart will fail unless `-f \ --force` flag is provided.
- :warning: Use `--force` with caution. Mounted volumes **will not** be moved to another ship. Static ports collision will result in service being stopped, and **not restarted**.

### Improvements
- Nicified `armada restart` warning/error output.

## 0.17.0 (2016-04-29)

### :warning: **UPGRADE WARNING** :warning:
Due to changes in armada internal API, all armada agents within the same cluster need to be upgraded, otherwise
remote runs and restarts will not work.

### Features
- Local haproxy binds both on IPv4 and IPv6.
- Default memory limit (both resident and swap) for services can now be customized per host. E.g. Add line
`DEFAULT_CONTAINER_MEMORY_LIMIT=512M` to `/etc/default/armada` on host.

### Improvements
- Set 0.5s timeout for fetching armada agents' versions in `armada info`.
- `$CONFIG_PATH` environment variable inside microservice (and mounted volumes for these configs) are now updated during
`armada restart` to pick up the new config directories.

## 0.16.1 (2016-04-04)

### Bug fixes:
- Fixed incorrect detection of dev environment during service recovery.

## 0.16.0 (2016-03-25)

### Features
- `armada run` adds configs to `CONFIG_PATH` for the renamed microservice name in addition to image name.
- Config directories provided with `armada run -c/--config` are additionally appended with combinations of `--env`
and `--app_id` when generating `CONFIG_PATH`.

### Bug fixes
- Fix bug with not recovering services run before armada 0.15.0.

## 0.15.0 (2016-03-22)

### Features
- Introduced resource limiting parameters to `armada run` command. These parameters accept same values as their respective docker parameters.
    - --cpu-shares
    - --memory
    - --memory-swap
    - --cgroup-parent


### Improvements
- `hermes` for python has been moved to `pypi` repository. It is available for download with `pip install armada` and can be imported with `from armada import hermes` command.
- As a result built-in `hermes` has been marked as deprecated.
- Suggest working workaround for accessing http dockyards in case they are running behind main-haproxy.

## 0.14.1 (2016-03-07)

### Bug fixes
- Fixed detection of development environment.
- Fix bug with pulling image without explicit tag.

## 0.14.0 (2016-02-23)

### Features
- Support for [dockyard-v2](https://github.com/armadaplatform/dockyard-v2) (based on docker registry v2).
- Support for HTTPS dockyards with self-signed certificates.
- Detect not working remote HTTP dockyards and suggest workaround.
- Added microservice_go base image.

### Improvements
- Upgrade Consul from version 0.6.0 to 0.6.3.
- Run Consul using os.execv instead of spawning new process, which makes Consul's logs available in supervisor.
- Store sorted container parameters in `/opt/armada/` on Ship, to make checking differences between versions easier.
- Allow microservices' local haproxy to forward http connections with Host header.

### Bug fixes
- Passing `-d local` to `armada run` in Armada vagrant box does not break detection of development environment.
- [Vagrant](https://github.com/armadaplatform/vagrant "Armada Vagrant") origin_dockyard_address parameter works properly with local dockyards by running localhost proxy.

## 0.13.1 (2016-01-08)

### Bug fixes
- `armada ssh` invoked for remote services, that were rebuilt from microservice image v0.13.0 threw
`KeyError - '22/tcp'`.

## 0.13.0 (2015-12-30)

### Features
- Upgrade Consul from version 0.4.1 to 0.6.0.

### Improvements
- Don't expose port 22 and install openssh-server in microservice image anymore.
- Increase timeouts to docker server, dockyards and local haproxy.
- Remove hack for manual installing pip on Ubuntu.

### :warning: **UPGRADE WARNING** :warning:

Due to Consul upgrade, the promoted Armada agents (leaders and commanders) with version >= 0.13.0 cannot be mixed with
older versions.
There is a 15 minute window for upgrade. See more details:
https://github.com/hashicorp/consul/commit/f53bd94dc334c56968ac4e33e19d9ca6a2b5aa22

## 0.12.0 (2015-12-28)

### Features
- You can now pass options `-t/--tty` and `-i/--interactive` to `armada ssh`, which translate to corresponding
`docker exec` options. Also the default behavior has been changed in case the command is provided. Both options,
`-t` and `-i`, are turned off then.
- New microservice template for `armada create` - python3 (based on [bottle](http://bottlepy.org/)).

### Improvements
- Added link to docker docs about configuring insecure registries when connection to such registry is attempted.
(Contributed by [ryneeverett](https://github.com/ryneeverett))

### Bug fixes
- Fix bug with `armada ssh` always returning exit code 0.
- Fix recovering services after Docker/host restart.

## 0.11.1 (2015-12-17)

### Improvements
- Start local_magellan only when require_service is invoked.

### Bug fixes
- Fix hanging Armada on start, when using Docker version 1.9.1.
- Use commands `python2` and `pip2` on Armada host in case the default python is 3.x.
(Contributed by [ryneeverett](https://github.com/ryneeverett))
- Fix detection of external Armada IP on some systems.
(Contributed by [ryneeverett](https://github.com/ryneeverett))

## 0.11.0 (2015-12-07)

### Improvements
- Increased size of health checks logs. (previously: 2 files up to 1MB each. now: 3 files up to 5MB each)
- Revamped `armada ssh` command by moving `sshd` process from microservice image to Armada container.
    - `docker exec` is now used to enter a container on the same host.
    - In order to enter container on another host, ssh is used to connect to remote Armada container.
    - **Containers created with new microservice image won't be accessible without updating Armada**

### Features
- Added microservice_python3.5 base image.


## 0.10.0 (2015-11-12)

### Improvements
- Default health-check (main-port-open) passes when main service's port is open on any interface, and not only 127.0.0.1. (Contributed by [zerofudge](https://github.com/zerofudge))


- Changed `armada create` command syntax from `armada create {template_name} [--name/-n {service_name}]` to `armada create {service-name} [--base-template/-b {template}]`. Default value for `--base-template` is  `python`.
- Available templates are `python` and `node`. E.g.: `armada create my-service -b node` creates a directory with new service called `my-service` based on `node` template (using `microservice_node` base image).

### Features
- Added node.js microservice template to `armada create` command with `node` as a base_template name.

### Bug fixes
- `armada create` command now works properly in any directory on system.

## 0.9.0 (2015-10-21)

### Features
- Armada supports registering UDP services in catalog.
- New armada service - [example-udp](https://github.com/armadaplatform/example-udp) that demonstrates registering UDP
services and discovering it by others.

## 0.8.0 (2015-09-22)

### Features
- New base image `microservice_node4` with node v4.0.0.
- New armada service - [Static file server](https://github.com/armadaplatform/static-file-server)

### Improvements
- Changed order of steps executed on armada restart. Instead of stop, pull, run now we do: pull, stop, run so that
service's downtime is minimized.
- Changed way of determining time when Docker daemon started to prevent unnecessary services' recoveries.


## 0.7.4 (2015-09-16)

### Improvements
- Updated node.js in `microservice_node` base image from v0.10.25 to v0.12.7.

## 0.7.3 (2015-09-14)

### Bug fixes
- Fixed a bug where microservices run with --rename parameter did not recover properly.
- Fixed docker error when running restart-armada development script.

## 0.7.2 (2015-09-03)

### Improvements
-  PID-1 zombie reaping problem resolved. Changed main system process inside containers from microservice init script to supervisor.
Containers will no longer spawn multiple zombie processes e.g. after armada ssh command.
- Note: **This change requires rebuilding services created before this fix.**


## 0.7.1 (2015-08-28)

#### Improvements
- Access Consul agent from Armada commands by localhost, instead of private Docker IP, as it sometimes causes hanging requests.


## 0.7.0 (2015-08-21)

#### Features
- Added parameter `--rename` to `armada run`.


## 0.6.5 (2015-08-06)

#### Improvements
- `armada stop` and `armada restart` will now display microservice name and container id regardless of passed parameter.


## 0.6.4 (2015-07-17)

#### Bug fixes
- Fixed `armada run` command on systems running python 2.6.


## 0.6.3 (2015-07-01)

#### Improvements
- `armada run` now waits for the dockyards list to be restored from `runtime_settings.json`.


## 0.6.2 (2015-06-24)

#### Bug fixes
- Fixed setting first dockyard as the default.


## 0.6.1 (2015-06-19)

#### Bug fixes
- Fixed race condition bug when one service wants to discover multiple other services using local magellan (e.g. multiple
    calls to require_service.py in supervisor configs).

#### Improvements
- Removed deprecated way of doing health checks. Armada doesn't have to run health checks by itself anymore.
Instead, services based on `microservice` image report health checks directly to Consul.


## 0.6.0 (2015-05-14)

#### Features
- Added custom health checks support for multi-service containers. Custom health check can be now specified with register_in_service_discovery script (-c / --health-check).

#### Improvements
- If CONFIG_DIR environment variable is defined in Dockerfile, then hermes automatically will update CONFIG_PATH to include provided directory.
- Armada commands now work properly with multi-service containers.
- Services' initial health check is no longer set to 'passing'. Instead health checks are run on startup after a slight delay.

## 0.5.3 (2015-05-11)

#### Bug fixes
- Updated docker-py library to 1.2.2 to fix authorization bug on docker pull.


## 0.5.2 (2015-05-07)

#### Improvements
- `armada recover` now retries up to 5 times and returns list of those that failed to restart within retry limit if there were any.


## 0.5.1 (2015-04-29)

#### Improvements
- Insert environment variables to crontab inside the container, one by one, to avoid not passing variables at all if one hits the crontab's limit of 1000 characters per line and warn if that's the case.
- Skip passing internal Armada's environment variables to crontab.


## 0.5.0 (2015-04-22)

#### Improvements
- Compatibility with docker version > 1.3.0 . Warning with help message will appear when trying to use insecure registry (dockyard over HTTP).

- Improved local magellan with 'env inheritance' denoted by '/'. Now when using require_service script, if a service with matching MICROSERVICE_ENV is not found, local magellan will look for a service with 'parent' MICROSERVICE_ENV.
e.g. if running a service with `production/my-app/my-name` env, local magellan will first look for a service with `production/my-app/my-name` env, then `production/my-app` env and finally `production` env.


## 0.4.4 (2015-03-10)

#### Improvements
- `microservice` - Local magellan now configures HAProxy to actively refuse connections when required service is not available.


## 0.4.3 (2015-03-06)

#### Bug fixes
- Fixed `armada shutdown` behaviour on CentOS.


## 0.4.2 (2015-02-27)

#### Bug fixes
- Local magellan: `require_service.py` can now be overridden with empty `--env` or `--app_id`.


## 0.4.1 (2015-02-12)

#### Bug fixes
- Fixed running containers from dockyards with authentication required, once again.


## 0.4.0 (2015-02-11)

#### Features
- Changed domain `armada.ganymede.eu` to `armada.sh`.
- `service armada stop` now doesn't remove runtime info about ship name, dockyards and connected ships.
Previous behaviour is available with command `service armada shutdown`.
- New base image: `microservice_python3`.

#### Bug fixes
- Fixed `armada push` for default dockyard.


## 0.3.3 (2015-01-26)

#### Bug fixes
- Fixed running containers from dockyards with authentication required.


## 0.3.2 (2015-01-22)

#### Bug fixes
- 'Created (UTC)' column in `armada list -u` now shows time in UTC instead of local.

#### Improvements
- No retries when `docker build` command failed, as it usually indicates problem with Dockerfile or that user pressed Ctrl + c.


## 0.3.1 (2015-01-21)

#### Bug fixes
- `armada push` now handles dockyards' authentication.


## 0.3.0 (2015-01-21)

#### Features
- `armada stop` and `armada restart` now have option `-a`/`--all` to restart all services with given name.

#### Bug fixes
- Detect failures of pulling from dockyards and return non-zero code to system.


## 0.2.0 (2015-01-19)

#### Features
- Armada agent now recovers local running containers after machine failure or docker daemon restart.
- `armada recover` command for manual recovery of running services from previously saved state.
- Running containers' parameters are backed up every 1h in `/opt/armada/saved_containers_backup/` for `armada recover` use.


## 0.1.0

Initial Armada version.
