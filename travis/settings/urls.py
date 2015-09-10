from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^', include('geokey.core.urls')),
    url(r'^', include('geokey_export.urls', namespace='geokey_export')),
)
