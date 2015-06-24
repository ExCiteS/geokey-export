import os
del os.link

from distutils.core import setup

setup(
    # Application name:
    name="geokey_export",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Patrick Rickles",
    author_email="p.rickles@ucl.ac.uk",

    # Packages
    packages=["geokey_export"],

    # Include additional files into the package
    include_package_data=True,

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[

    ],
)
