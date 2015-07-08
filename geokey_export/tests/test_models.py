from django.utils import timezone
from django.test import TestCase

from ..models import Export
from .model_factories import ExportFactory


class TemplateTagsTest(TestCase):
    def test_is_expired(self):
        export = Export(expiration=timezone.now())
        self.assertTrue(export.is_expired())

        export = Export()
        self.assertFalse(export.is_expired())

    def test_expire(self):
        export = ExportFactory.create(name='Test')
        self.assertFalse(export.is_expired())

        export.expire()
        self.assertTrue(export.is_expired())
