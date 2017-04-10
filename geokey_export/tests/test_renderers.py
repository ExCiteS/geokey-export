"""Tests for renderers of contributions (observations)."""

import json

from django.test import TestCase

from ..renderers import CSVRenderer


class CSVRendererTest(TestCase):

    def setUp(self):
        self.data = [
        {
            'display_field':
                {'value': u'456565', 'key': u'name'},
            'media': [],
            'expiry_field': None,
            'comments': [{
                'id': 153,
                'respondsto': None,
                'created_at': u'2017-04-07T16:03:05.445019Z',
                'text': u'text_template1',
                'isowner': True,
                'creator': {'id': 3, 'display_name': u'c.grillo'},
                'review_status': None,
                'responses': [{
                    'id': 555,
                    'respondsto': 153,
                    'created_at': u'2017-04-07T18:03:05.445019Z',
                    'text': u'text_responses1',
                    'isowner': True,
                    'creator': {'id': 3, 'display_name': u'c.grillo_example'},
                    'review_status': None,
                    'responses': [{
                        'id': 232,
                        'respondsto': 555,
                        'created_at': u'2017-04-08T16:03:05.445019Z',
                        'text': u'text_responses11',
                        'isowner': True,
                        'creator': {'id': 3, 'display_name': u'c.grillo_test'},
                        'review_status': None,
                        'responses': {}
                    }]
                }]

            }],
            'properties': {u'surname': u'pepepo5'},
            'meta':
                {
                'status': u'active',
                'num_media': 0,
                'isowner': True,
                'version': 1,
                'updator': None,
                'creator': {'display_name': u'c.grillo', 'id': 3},
                'num_comments': 1,
                'created_at': '2017-04-07 15:19:14.901149+00:00',
                'category':
                    {
                    'symbol': None,
                    'colour': u'#0033ff',
                     'description': u'',
                     'id': 81,
                     'name': u'sinquerer'
                    },
                'updated_at': '2017-04-07 15:19:14.901174+00:00'},
                'location':
                    {
                    'geometry': u'{ "type": "Point", "coordinates": [ -3.8671875, 15.792253570362446 ] }',
                    'description': None,
                    'id': 46,
                    'name': None},
                'id': 41,
        }
        ]

    def test_render(self):
        """Test for render."""
        renderer = CSVRenderer()
        result = renderer.render(self.data)

        self.assertTrue('geom' in result)

    def test_render_comments(self):
        """Test for render_comments."""
        renderer = CSVRenderer()
        result = renderer.render_comments(self.data)

        self.assertTrue('comment_id' in result)

    def test_render_mediafiles(self):
        """Test for render_mediafiles."""
        renderer = CSVRenderer()
        result = renderer.render_mediafiles(self.data)

        self.assertTrue('file_id' in result)
        self.assertTrue('file_type' in result)
