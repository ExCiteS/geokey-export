#!/usr/bin/env python

import os
del os.link

from setuptools import setup, find_packages


setup(
    name='geokey-export',
    version='0.1.0',
    author='Patrick Rickles',
    author_email='p.rickles@ucl.ac.uk',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),
    include_package_data=True,
)
