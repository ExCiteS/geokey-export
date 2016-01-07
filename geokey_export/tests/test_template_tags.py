from datetime import datetime
from django.test import TestCase
from django.template.defaultfilters import date as filter_date

from ..templatetags import export_tags
from ..models import Export


class TemplateTagsTest(TestCase):

    def test_expiry(self):
        export = Export(isoneoff=True)
        self.assertEqual(export_tags.expiry(export), 'One off')

        export = Export(expiration=datetime.now())
        self.assertEqual(
            export_tags.expiry(export),
            filter_date(export.expiration, 'd F, Y H:i')
        )

        export = Export(isoneoff=False)
        self.assertEqual(export_tags.expiry(export), 'Never')
