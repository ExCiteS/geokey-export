from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import ExportDelete


class UrlTest(TestCase):

    def test_delete_export(self):
        self.assertEqual(
            reverse('geokey_export:export_delete', kwargs={'export_id': 1}),
            '/admin/export/1/delete/'
        )

        resolved = resolve('/admin/export/1/delete/')
        self.assertEqual(resolved.func.func_name, ExportDelete.__name__)
        self.assertEqual(resolved.kwargs['export_id'], '1')
