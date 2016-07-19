# Armada

Armada is a complete solution for development, deployment, configuration and discovery of microservices.

Armada is more than just a tool, it defines conventions and good practices designed towards making
your platform more service oriented.


# Documentation

* Main Armada website: [http://armada.sh](http://armada.sh)
* Getting started: [http://armada.sh/intro](http://armada.sh/intro)
* Various Armada guides: [http://armada.sh/docs](http://armada.sh/docs)


# Repository overview

* [armada_backend/](armada_backend/) - Armada scripts that are run inside main `armada` container.
    They provide [Armada API](armada_backend/armada_api.py) which is used by Armada CLI.

* [armada_command/](armada_command/) - Armada command line interface. It is run on Armada ship and is a primary
    way to manage containers in the Armada cluster.

* [docker-containers/](docker-containers/) - Base microservice Docker images for various platforms (python, php, nodejs).

* [keys/](keys/) - Private SSH key that can be used to ssh into containers based on `microservice` image.

* [microservice_templates/](microservice_templates/) - Templates that can serve as a base for creating new
    Armada microservices. This repository is used by `armada create` command.

# Running tests

In the root directory of the repository run:

    python -m tests.unit_tests

# Workflow for Armada development:

1. $ vagrant up
2. $ vagrant ssh
3. Make changes in armada source code on your hard drive in directory that contains this Vagrantfile.
   It is in sync with /opt/armada-src in Vagrant.
   Autoreload of [Armada API](armada_backend/armada_api.py) is by default enabled.
4. Test changes.
5. $ armada push armada -d [dockyard]