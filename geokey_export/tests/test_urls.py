from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import (
    IndexPage, ExportOverview, ExportCreate, ExportDelete,
    ExportGetCategories, ExportGetContributions, ExportToRenderer
)


class UrlTest(TestCase):

    def test_index_page(self):
        self.assertEqual(reverse('geokey_export:index'), '/admin/export/')

        resolved = resolve('/admin/export/')
        self.assertEqual(resolved.func.func_name, IndexPage.__name__)

    def test_export_overview(self):
        self.assertEqual(
            reverse('geokey_export:export_overview', kwargs={'export_id': 1}),
            '/admin/export/1/'
        )

        resolved = resolve('/admin/export/1/')
        self.assertEqual(resolved.func.func_name, ExportOverview.__name__)
        self.assertEqual(resolved.kwargs['export_id'], '1')

    def test_export_create(self):
        self.assertEqual(
            reverse('geokey_export:export_create'),
            '/admin/export/create/'
        )

        resolved = resolve('/admin/export/create/')
        self.assertEqual(resolved.func.func_name, ExportCreate.__name__)

    def test_delete_export(self):
        self.assertEqual(
            reverse('geokey_export:export_delete', kwargs={'export_id': 1}),
            '/admin/export/1/delete/'
        )

        resolved = resolve('/admin/export/1/delete/')
        self.assertEqual(resolved.func.func_name, ExportDelete.__name__)
        self.assertEqual(resolved.kwargs['export_id'], '1')

    def test_export_get_categories(self):
        self.assertEqual(
            reverse(
                'geokey_export:export_get_categories',
                kwargs={'project_id': 1}
            ),
            '/admin/export/projects/1/categories/'
        )

        resolved = resolve('/admin/export/projects/1/categories/')
        self.assertEqual(
            resolved.func.func_name,
            ExportGetCategories.__name__
        )
        self.assertEqual(resolved.kwargs['project_id'], '1')

    def test_export_get_contributions(self):
        self.assertEqual(
            reverse(
                'geokey_export:export_get_contributions',
                kwargs={'project_id': 1, 'category_id': 2}
            ),
            '/admin/export/projects/1/categories/2/'
        )

        resolved = resolve('/admin/export/projects/1/categories/2/')
        self.assertEqual(
            resolved.func.func_name,
            ExportGetContributions.__name__
        )
        self.assertEqual(resolved.kwargs['project_id'], '1')
        self.assertEqual(resolved.kwargs['category_id'], '2')

    def test_geojson(self):
        self.assertEqual(
            reverse(
                'geokey_export:export_to_renderer',
                kwargs={'urlhash': 12345}
            ),
            '/admin/export/12345'
        )

        resolved = resolve('/admin/export/12345')
        self.assertEqual(
            resolved.func.func_name,
            ExportToRenderer.__name__
        )
        self.assertEqual(resolved.kwargs['urlhash'], '12345')
