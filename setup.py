#!/usr/bin/env python
# coding=utf-8

#
# To publish package release
# python setup.py sdist upload -r pypi
#

from setuptools import setup

setup(
    name='army',
    version='0.1.0',
    description='Arm cross compiling toolset',
    url='https://github.com/turdusmerula/army/',
    author='Sebastien Besombes',
    license='GPLv3',

#     scripts=['army.py'],
    packages=['army'],
#     package_data={
#         '' : ['*'],
#         'army.library-template': ['*'], 
#         'plugin-template': ['*'], 
#         'army.project-template': ['*'], 
#         },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'army = army.army:main',
        ]
    },
    zip_safe=False, # force egg extraction
    
    install_requires=[
        'tornado',      # template manager
        'gitpython',    # git repository manager
        'toml',         # toml files
        'click',
        'cmake',
        'schema',
    ],
)

