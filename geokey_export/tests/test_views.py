from django.test import TestCase
from django.http import HttpRequest
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.gis.geos import GEOSGeometry

from rest_framework.test import APIRequestFactory

from geokey.core.tests.helpers import render_helpers
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey import version
from geokey.contributions.renderer.geojson import GeoJsonRenderer
from geokey.contributions.renderer.kml import KmlRenderer

from ..views import (
    IndexPage, ExportCreate, ExportOverview, ExportDelete,
    ExportGetProjectCategories, ExportGetProjectCategoryContributions,
    ExportGetExportContributions, ExportToRenderer
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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)


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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        self.request.method = 'POST'

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')
        self.assertEqual(Export.objects.count(), 0)

    def test_post_with_some_dude(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{'project': project})

        self.request.method = 'POST'
        self.request.POST = {
            'name': 'Name',
            'project': project.id,
            'category': category.id,
            'expiration': 'one_off',
            'geometry': '{"type": "Polygon","coordinates": [['
                        '[-0.508,51.682],[-0.53,51.327],[0.225,51.323],'
                        '[0.167,51.667],[-0.508,51.682]]]}'
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
        self.assertEqual(reference.bounding_box.geom_type, 'Polygon')
        self.assertEqual(
            reference.bounding_box.json,
            GEOSGeometry(self.request.POST.get('geometry')).json
        )


class ExportOverviewTest(TestCase):
    def setUp(self):
        self.view = ExportOverview.as_view()
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.user = AnonymousUser()
        self.export = ExportFactory.create()
        self.data = {
            'geometry': '{"type": "Polygon","coordinates": [['
                        '[-0.508,51.682],[-0.53,51.327],[0.225,51.323],'
                        '[0.167,51.667],[-0.508,51.682]]]}',
            'expiration': 'one_off'
        }

    def test_get_with_anonymous(self):
        response = self.view(self.request, export_id=self.export.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

    def test_post_with_anonymous(self):
        self.request.method = 'POST'
        self.request.POST = self.data
        response = self.view(self.request, export_id=self.export.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/admin/account/login/?next=')

        reference = Export.objects.get(pk=self.export.id)
        self.assertFalse(reference.isoneoff)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)
        self.assertEqual(reference.bounding_box.geom_type, 'Polygon')
        self.assertEqual(
            reference.bounding_box.json,
            GEOSGeometry(self.request.POST.get('geometry')).json
        )

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)


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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)
        self.assertEqual(Export.objects.count(), 1)


class ExportGetProjectCategoriesTest(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        CategoryFactory.create(**{'project': self.project})

        self.view = ExportGetProjectCategories.as_view()
        self.url = reverse(
            'geokey_export:export_get_project_categories',
            kwargs={'project_id': self.project.id}
        )
        self.request = APIRequestFactory().get(self.url)
        self.request.user = AnonymousUser()

    def test_get_with_admin(self):
        self.request.user = self.project.creator
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_when_project_is_inactive(self):
        self.request.user = self.project.creator
        self.project.status = 'inactive'
        self.project.save()
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_when_project_is_private(self):
        self.request.user = self.project.creator
        self.project.isprivate = True
        self.project.save()
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 200)

    def test_get_with_some_dude(self):
        self.request.user = UserFactory.create()
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 404)

    def test_get_when_project_does_not_exist(self):
        self.request.user = self.project.creator
        self.project.delete()
        response = self.view(self.request, project_id=self.project.id)
        self.assertEqual(response.status_code, 404)


class ExportGetProjectCategoryContributionsTest(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        self.category = CategoryFactory.create(**{'project': self.project})

        self.view = ExportGetProjectCategoryContributions.as_view()
        self.url = reverse(
            'geokey_export:export_get_project_category_contributions',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id
            }
        )
        self.request = APIRequestFactory().get(self.url)
        self.request.user = AnonymousUser()

    def test_get_with_admin(self):
        self.request.user = self.project.creator
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 200)

    def test_get_when_project_is_inactive(self):
        self.request.user = self.project.creator
        self.project.status = 'inactive'
        self.project.save()
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 200)

    def test_get_when_project_is_private(self):
        self.request.user = self.project.creator
        self.project.isprivate = True
        self.project.save()
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 200)

    def test_get_when_category_is_inactive(self):
        self.request.user = self.project.creator
        self.category.status = 'inactive'
        self.category.save()
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 200)

    def test_get_with_some_dude(self):
        self.request.user = UserFactory.create()
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 404)

    def test_get_when_project_does_not_exist(self):
        self.request.user = self.project.creator
        self.project.delete()
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 404)

    def test_get_when_category_does_not_exist(self):
        self.request.user = self.project.creator
        self.category.delete()
        response = self.view(
            self.request,
            project_id=self.project.id,
            category_id=self.category.id
        )
        self.assertEqual(response.status_code, 404)


class ExportGetExportContributionsTest(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()
        self.category = CategoryFactory.create(**{'project': self.project})
        self.export = ExportFactory.create(**{
            'project': self.project,
            'category': self.category
        })

        self.view = ExportGetExportContributions.as_view()
        self.url = reverse(
            'geokey_export:export_get_export_contributions',
            kwargs={
                'export_id': self.export.id
            }
        )
        self.request = APIRequestFactory().get(self.url)
        self.request.user = AnonymousUser()

    def test_get_with_project_admin(self):
        self.request.user = self.project.creator
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 403)

    def test_get_with_export_creator(self):
        self.request.user = self.export.creator
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 200)

    def test_get_when_export_creator_is_not_project_admin_anymore(self):
        self.request.user = self.export.creator
        self.project.creator = UserFactory.create()
        self.project.save()
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 200)

    def test_get_when_project_is_inactive(self):
        self.request.user = self.export.creator
        self.project.status = 'inactive'
        self.project.save()
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 200)

    def test_get_when_project_is_private(self):
        self.request.user = self.export.creator
        self.project.isprivate = True
        self.project.save()
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 200)

    def test_get_when_category_is_inactive(self):
        self.request.user = self.export.creator
        self.category.status = 'inactive'
        self.category.save()
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 200)

    def test_get_with_some_dude(self):
        self.request.user = UserFactory.create()
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 403)

    def test_get_when_export_does_not_exist(self):
        self.request.user = self.export.creator
        self.export.delete()
        response = self.view(self.request, export_id=self.export.id)
        self.assertEqual(response.status_code, 404)


class ExportToRendererTest(TestCase):
    def setUp(self):
        self.view = ExportToRenderer.as_view()
        self.request = HttpRequest()
        self.request.META['SERVER_NAME'] = 'test-server'
        self.request.META['SERVER_PORT'] = '80'
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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)

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
        self.assertEqual(response.status_code, 200)
        response = render_helpers.remove_csrf(unicode(response.content))
        self.assertEqual(response, rendered)
