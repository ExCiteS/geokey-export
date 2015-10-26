geokey-export
=============

.. image:: https://travis-ci.org/ExCiteS/geokey-export.svg?branch=master
    :target: https://travis-ci.org/ExCiteS/geokey-export

Export data from GeoKey into various formats
    
Currently supported formats:

- KML
- GeoJSON

Install
-------

Install the extension:

.. code-block:: console

    cd geokey-export
    pip install -e .


Add the package to installed apps:

.. code-block:: console

    INSTALLED_APPS += (
        ...
        'geokey_export'
    )

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_export

Copy static files:

.. code-block:: console

    python manage.py collectstatic

You're ready to go now.

Test
----

Run tests:

.. code-block:: console

    python manage.py test geokey_export

Test Coverage:

.. code-block:: console

    coverage run --source=geokey_export manage.py test geokey_export
    coverage report -m --omit=*/tests/*,*/migrations/*
