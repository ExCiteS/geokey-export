import os
del os.link

from setuptools import setup, find_packages

setup(
    # Application name:
    name="geokey_export",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Patrick Rickles",
    author_email="p.rickles@ucl.ac.uk",

    # Packages
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*']),

    # Include additional files into the package
    include_package_data=True,
)
