from geokey.extensions.base import register
register(
    'geokey_export',
    'GeoKey Export',
    display_admin=True,
    superuser=False
)
