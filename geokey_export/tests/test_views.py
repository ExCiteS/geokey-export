from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from geokey.users.tests.model_factories import UserF

from ..views import ExportDelete
from ..models import Export

from .model_factories import ExportFactory


class ExportDeleteTest(TestCase):
    def setUp(self):
        self.view = ExportDelete.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        self.export = ExportFactory.create()

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        response = self.view(self.request, export_id=self.export.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

    def test_get_with_owner(self):
        self.request.user = self.export.creator
        response = self.view(self.request, export_id=self.export.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/export/')
        self.assertEqual(Export.objects.count(), 0)

    def test_get_with_some_dude(self):
        user = UserF.create()
        self.request.user = user
        response = self.view(self.request, export_id=self.export.id).render()

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'You must be creator of the export.',
                'error': 'Permission denied.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Export.objects.count(), 1)
