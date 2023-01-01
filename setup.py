#!/usr/bin/env python3

from setuptools import setup

#1: python setup.py sdist
#2: twine upload dist/* --repository-url https://upload.pypi.org/legacy/

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='EasyModbus',
    packages = ['easymodbus'],
    version      = '2.0.0',
    license      = 'MIT',
    author       = 'Stefan Rossmann',
    author_email = 'info@rossmann-engineering.de',
    url          = 'http://www.easymodbustcp.net',#'https://github.com/rossmann-engineering/EasyModbusTCP.PY',
    long_description=long_description,
    description='THE standard library for Modbus RTU and Modbus TCP - See www.EasyModbusTCP.NET for documentation',
    long_description_content_type='text/markdown',
    install_requires=[
          'pyserial'
      ],
    keywords='easymodbus modbus serial RTU TCP EasyModbusTCP',
    classifiers=[
       'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ]
)