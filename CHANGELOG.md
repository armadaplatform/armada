# Changelog

## Unreleased

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
