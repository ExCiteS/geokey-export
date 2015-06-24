geokey-export
=============

Testing
-------

Run tests:

.. code-block:: console

    python manage.py test geokey_export --nocapture --nologcapture

Test Coverage:

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

Then, link the URLs into `urls.py`:

.. code-block:: console

    urlpatterns = patterns(
        ...
        url(r'^', include('geokey_export.urls', namespace='geokey_export')),
    )

You're ready to go now.
