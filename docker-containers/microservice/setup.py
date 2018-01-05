from setuptools import setup

from microservice.version import VERSION

setup(
    name='armada-microservice',
    description='Microservice package - base of all armada microservices. CLI for communicating between '
                'microservice and armada.',
    version=VERSION,
    url='https://github.com/armadaplatform/armada-microservice',
    author='Cerebro',
    author_email='cerebro@ganymede.eu',
    packages=[
        'microservice',
        'microservice.common',
        'microservice.local_magellan',
    ],
    scripts=[
        'microservice/microservice',
    ],
    install_requires=[
        'docker==2.4.2',
        'requests==2.9.1',
        'armada',
    ],
)
