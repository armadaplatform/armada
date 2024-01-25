from microservice.version import VERSION
from setuptools import setup

setup(
    name='armada-microservice',
    description='Microservice package - base of all armada microservices. CLI for communicating between '
                'microservice and armada.',
    version=VERSION,
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
        'requests==2.29.0',
        'armada',
        'pyopenssl',
    ],
)
