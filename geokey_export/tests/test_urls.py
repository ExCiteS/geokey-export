from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import (
    IndexPage, ExportOverview, ExportCreate, ExportDelete,
    ExportCreateUpdateCategories, ExportToRenderer
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

    def test_export_categories(self):
        self.assertEqual(
            reverse(
                'geokey_export:export_create_update_categories',
                kwargs={'project_id': 1}
            ),
            '/admin/export/1/categories/'
        )

        resolved = resolve('/admin/export/1/categories/')
        self.assertEqual(
            resolved.func.func_name,
            ExportCreateUpdateCategories.__name__
        )
        self.assertEqual(resolved.kwargs['project_id'], '1')

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
