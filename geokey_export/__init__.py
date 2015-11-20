from geokey.extensions.base import register


register(
    'geokey_export',
    'Export',
    display_admin=True,
    superuser=False
)
