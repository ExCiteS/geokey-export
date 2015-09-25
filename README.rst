geokey-export
=============

.. image:: https://travis-ci.org/ExCiteS/geokey-export.svg?branch=master
    :target: https://travis-ci.org/ExCiteS/geokey-export

Testing
-------

Run tests:

.. code-block:: console

    python manage.py test geokey_export --nocapture --nologcapture

Test Coverage:

.. code-block:: console

    coverage run --source=geokey_export manage.py test geokey_export --nocapture --nologcapture
    coverage report -m --omit=*/tests/*,*/migrations/*

Install
-------

Install the extension. Move to the root directory of your package and install for development.

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

    python manage.py migrate

Copy static files:

.. code-block:: console

    python manage.py collectstatic

You're ready to go now.
