from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey import version
from geokey.contributions.renderer.geojson import GeoJsonRenderer
from geokey.contributions.renderer.kml import KmlRenderer

from ..views import (
    IndexPage, ExportCreate, ExportOverview, ExportDelete,
    ExportCreateUpdateCategories, ExportToRenderer
)
from ..models import Export

from .model_factories import ExportFactory


class IndexPageTest(TestCase):

    def setUp(self):
        self.view = IndexPage.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

    def test_get_with_anonymous(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

    def test_get_with_some_dude(self):
        user = UserFactory.create()
        export = ExportFactory.create(**{'creator': user})
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'export_index.html',
            {
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'exports': [export]
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)


class ExportCreateTest(TestCase):
    def setUp(self):
        self.view = ExportCreate.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()

    def test_get_with_anonymous(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

    def test_post_with_anonymous(self):
        self.request.method = 'POST'

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')
        self.assertEqual(Export.objects.count(), 0)

    def test_get_with_some_dude(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'export_create.html',
            {
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'projects': [project]
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_post_with_some_dude(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{'project': project})

        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'project': project.id,
            'category': category.id,
            'expiration': 'one_off'
        }
        self.request.user = user

        response = self.view(self.request)

        self.assertEqual(Export.objects.count(), 1)
        reference = Export.objects.first()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['location'],
            '/admin/export/%s/' % reference.id
        )


class ExportOverviewTest(TestCase):
    def setUp(self):
        self.view = ExportOverview.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        self.export = ExportFactory.create()
        self.data = {
            'expiration': 'one_off'
        }

    def test_get_with_anonymous(self):
        response = self.view(self.request, export_id=self.export.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

    def test_post_with_anonymous(self):
        self.request.method = 'POST'
        self.request.POST = self.data
        response = self.view(self.request, export_id=self.export.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

        reference = Export.objects.get(pk=self.export.id)
        self.assertFalse(reference.isoneoff)

    def test_get_with_owner(self):
        user = self.export.creator
        self.request.user = user

        response = self.view(self.request, export_id=self.export.id).render()

        rendered = render_to_string(
            'export_overview.html',
            {
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'export': self.export
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_post_with_owner(self):
        user = self.export.creator
        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = self.data

        response = self.view(self.request, export_id=self.export.id).render()

        reference = Export.objects.get(pk=self.export.id)
        self.assertTrue(reference.isoneoff)

        rendered = render_to_string(
            'export_overview.html',
            {
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'export': reference
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_post_with_owner_expired(self):
        user = self.export.creator
        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = {
            'expiration': 'one_week'
        }

        response = self.view(self.request, export_id=self.export.id).render()

        reference = Export.objects.get(pk=self.export.id)
        self.assertFalse(reference.isoneoff)
        self.assertIsNotNone(reference.expiration)

        rendered = render_to_string(
            'export_overview.html',
            {
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'export': reference
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_get_with_some_dude(self):
        user = UserFactory.create()
        self.request.user = user

        response = self.view(self.request, export_id=self.export.id).render()

        rendered = render_to_string(
            'export_overview.html',
            {
                'error_description': 'You must be creator of the export.',
                'error': 'Permission denied.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_post_with_some_dude(self):
        user = UserFactory.create()
        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = self.data

        response = self.view(self.request, export_id=self.export.id).render()

        reference = Export.objects.get(pk=self.export.id)
        self.assertFalse(reference.isoneoff)

        rendered = render_to_string(
            'export_overview.html',
            {
                'error_description': 'You must be creator of the export.',
                'error': 'Permission denied.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_get_non_exisiting_export(self):
        user = UserFactory.create()
        self.request.user = user

        response = self.view(self.request, export_id=8923783903786).render()

        rendered = render_to_string(
            'export_overview.html',
            {
                'error_description': 'Export not found.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_post_non_exisiting_export(self):
        user = UserFactory.create()
        self.request.user = user
        self.request.method = 'POST'
        self.request.POST = self.data

        response = self.view(self.request, export_id=8923783903786).render()

        rendered = render_to_string(
            'export_overview.html',
            {
                'error_description': 'Export not found.',
                'error': 'Not found.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)


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
        user = UserFactory.create()
        self.request.user = user
        response = self.view(self.request, export_id=self.export.id).render()

        rendered = render_to_string(
            'base.html',
            {
                'error_description': 'You must be creator of the export.',
                'error': 'Permission denied.',
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version()
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Export.objects.count(), 1)


class ExportCreateUpdateCategoriesTest(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        CategoryFactory.create(**{'project': self.project})

        self.view = ExportCreateUpdateCategories.as_view()
        self.url = reverse(
            'geokey_export:export_create_update_categories',
            kwargs={'project_id': self.project.id}
        )
        self.request = APIRequestFactory().get(self.url)
        self.request.user = AnonymousUser()

    def test_get_with_admin(self):
        self.request.user = self.project.creator
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_with_some_dude(self):
        self.request.user = UserFactory.create()
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 404)


class ExportToRendererTest(TestCase):
    def setUp(self):
        self.view = ExportToRenderer.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        self.export = ExportFactory.create()

    def test_get_html(self):
        response = self.view(self.request, urlhash=self.export.urlhash)

        rendered = render_to_string(
            'export_access.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'export': self.export
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_get_geojson(self):
        response = self.view(
            self.request,
            urlhash=self.export.urlhash,
            format='json'
        )

        rendered = GeoJsonRenderer().render([])
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_get_kml(self):
        response = self.view(
            self.request,
            urlhash=self.export.urlhash,
            format='kml'
        )

        rendered = KmlRenderer().render([])
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_get_expired(self):
        self.export.expire()
        response = self.view(
            self.request,
            urlhash=self.export.urlhash,
            format='kml'
        )

        rendered = render_to_string(
            'export_access.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error_description': 'The export was not found in the database.',
                'error': 'Not found.'
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)

    def test_get_nonexisting(self):
        response = self.view(
            self.request,
            urlhash='783678ywqnjhd88893u289ue',
            format='kml'
        )

        rendered = render_to_string(
            'export_access.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'error_description': 'The export was not found in the database.',
                'error': 'Not found.'
            }
        )
        self.assertEqual(unicode(response.content), rendered)
        self.assertEqual(response.status_code, 200)
