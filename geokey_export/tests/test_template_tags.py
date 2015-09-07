from datetime import datetime
from django.test import TestCase

from ..templatetags import export_tags
from ..models import Export


class TemplateTagsTest(TestCase):

    def test_expiry(self):
        export = Export(isoneoff=True)
        self.assertEqual(export_tags.expiry(export), 'One off')

        export = Export(expiration=datetime.now())
        self.assertEqual(export_tags.expiry(export), export.expiration)

        export = Export(isoneoff=False)
        self.assertEqual(export_tags.expiry(export), 'Never')
