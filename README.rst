GeoKey Extension Boilerplate
============================

This is a boilerplate if you wish to create your own extension for `GeoKey <http://github.com/excites/geokey/>`__.

Customization quick start
-------------------------

To start a new extension using the boilerplate, follow the instructions.

`Download the extension <https://github.com/ExCiteS/geokey-extension-boilerplate/archive/master.zip>`__

Rename all occurences of `geokey_extension` with the name of your Python package (e.g. my_awesome_package) and `GeoKey Extension` with a title of your extension (e.g. My Extension). The latter one will be used in user interface if applicable. Don't forget to rename the directories accordingly.

Install the extension. Move to the root directory of your package and install for development.

.. code-block:: console

    cd geokey-extension
    pip install -e .


Add the package to installed apps:

.. code-block:: console

    INSTALLED_APPS += (
        ...
        'my_awesome_package'
    )

Then, link the URLs into `urls.py`:

.. code-block:: console

    urlpatterns = patterns(
        ...
        url(r'^', include('my_awesome_package.urls', namespace='my_awesome_package')),
    )

You're ready to go now.

Register the extension to the backend
-------------------------------------

You can add extension specific pages to GeoKey's adminstration. The link will then appear in the users dashboard under _Extensions_. Note, that GeoKey expects the landing page to your extension at the named URL pattern `my_awesome_package:index`.

To register the extension, open `__init__.py` in the app root and set

.. code-block:: console

    display_admin=True,

You can also restrict the extension to superusers of the system to be able to access the extension specific admin pages of your extension. Just set

.. code-block:: console

    superuser=True,


Get in touch
------------

Get in touch with `Oliver Roick <https://github.com/oliverroick>`__ if you have questions and suggestions.
