# -*- coding: utf-8 -*-

from setuptools import setup
from taskmq import __version__

setup(
    name='TaskMQ',
    version=__version__,
    author='Geoffrey Gueret',
    author_email='geoffrey@mailq.io',
    description='',
    long_description='',
    url='https://github.com/ggueret/taskmq',
    license='BSD',
    keywords='taskmq amqp task rpc',
    packages=['taskmq'],
    install_requires=['librabbitmq'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
