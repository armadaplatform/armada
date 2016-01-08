# Changelog

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
