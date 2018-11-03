from django.test import TestCase

from ..base import media_keys, comment_keys, keys_obs
from ..utils import (
    get_responses,
    get_fields,
    get_mediafiles,
    get_info_comment,
    create_observation_row
)


class UtilsTest(TestCase):

    def setUp(self):

        self.data = [
        {
        'display_field':
            {'value': u'456565', 'key': u'name'},
        'media': [],
        'expiry_field': None,
        'comments': [
            [('id', 153),
                ('respondsto', None),
                ('created_at', u'2017-04-07T16:03:05.445019Z'),
                ('text', u'text_template1'),
                ('isowner', True),
                ('creator', [('id', 3), ('display_name', u'c.grillo')]),
                ('review_status', None),
                ('responses', [
                    ('id', 155),
                    ('respondsto', None),
                    ('created_at', u'2017-04-07T16:03:10.005092Z'),
                    ('text', u'text_responses1'),
                    ('isowner', True),
                    ('creator', [('id', 3), ('display_name', u'c.grillo')]),
                    ('review_status', None), ('responses', [])])],
            [('id', 154),
                ('respondsto', None),
                ('created_at', u'2017-04-07T16:03:10.005092Z'),
                ('text', u'text_template2'),
                ('isowner', True),
                ('creator', [('id', 3), ('display_name', u'c.grillo')]),
                ('review_status', None), ('responses', [])
            ]
        ],
        'properties': {u'country': u'Island'},
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
        self.obs_id = self.data[0]['id']
        self.keys = keys_obs
        self.comment_keys = comment_keys

    def test_get_fields(self):
        """Test for get_fields method."""
        headers = get_fields(self.data)

        self.assertTrue('country' in headers)

    def test_get_info_comment(self):
        """Test for get_info_method."""
        comments = {
            'id': 153,
            'respondsto': None,
            'created_at': u'2017-04-07T16:03:05.445019Z',
            'text': u'text_template1',
            'isowner': True,
            'creator': {'id': 3, 'display_name': u'c.grillo'},
            'review_status': None,
            'responses': {}
        }

        comment_txt = get_info_comment(33, comments, self.comment_keys)

        self.assertTrue(comments['text'] in comment_txt)
        self.assertTrue(str(comments['id']) in comment_txt)
        self.assertTrue(comments['creator']['display_name'] in comment_txt)
        self.assertTrue(str(comments['creator']['id']) in comment_txt)

    def test_get_responses(self):
        """Test for get_responses."""
        comments2 = {
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

        }

        responses = get_responses(
            self.obs_id,
            comments2,
            1)

        comment_id = str(comments2['responses'][0]['id'])
        response_comment_id = str(comments2['responses'][0]['responses'][0]['id'])

        # self.assertTrue(str(comments['id']) in responses)
        self.assertEqual(2, len(responses))
        self.assertTrue(comment_id in responses[0])
        self.assertTrue(response_comment_id in responses[1])
        self.assertTrue(str('c.grillo_example') in responses[0])
        self.assertFalse(str('c.grillo_example') in responses[1])
        self.assertTrue(str('c.grillo_test') in responses[1])
        self.assertFalse(str('c.grillo_test') in responses[0])

    def test_create_observation_row(self):
        """Test for create_observation_row."""
        observation_txt = create_observation_row(self.data[0], self.keys)

        wkt_coordinates = 'POINT (-3.8671875 15.7922535)'
        display_name = self.data[0]['meta']['creator']['display_name']
        self.assertTrue(str(self.data[0]['id']) in observation_txt)
        self.assertTrue(wkt_coordinates in observation_txt)
        self.assertTrue(display_name in observation_txt)

    def test_get_mediafiles(self):
        """Test for get_mediafiles."""

        mediafiles = [{
            "id": 86,
            "name": "django-neg.sh-600x600",
            "description": None,
            "created_at": "2017-04-05T15:25:18.576273Z",
            "creator": {
                "id": 3,
                "display_name": "c.gisbert123"
            },
            "isowner": True,
            "url": "http://127.0.0.1:8000/assets/user-uploads/images/django-negsh-600x600.png",
            "thumbnail_url": "http://127.0.0.1:8000/assets/user-uploads/images/django-negsh-600x600.png.300x300_q85_crop.png",
            "file_type": "ImageFile"
        }, {
            "id": 87,
            "name": "costa",
            "description": None,
            "created_at": "2017-04-05T15:25:19.105646Z",
            "creator": {
                "id": 3,
                "display_name": "c.gisbert123"
            },
            "isowner": True,
            "url": "http://127.0.0.1:8000/assets/user-uploads/images/costa.png",
            "thumbnail_url": "http://127.0.0.1:8000/assets/user-uploads/images/costa.png.300x300_q85_crop.jpg",
            "file_type": "ImageFile"
        }]

        mediafiles_txt = get_mediafiles(
            self.obs_id,
            mediafiles[0],
            media_keys)

        self.assertTrue(str(mediafiles[0]['id']) in mediafiles_txt)
        self.assertTrue(mediafiles[0]['url'] in mediafiles_txt)
        self.assertFalse(mediafiles[1]['url'] in mediafiles_txt)
        self.assertTrue(mediafiles[0]['file_type'] in mediafiles_txt)
        self.assertFalse('VideoFile' in mediafiles_txt)

        mediafiles_txt2 = get_mediafiles(
            self.obs_id,
            mediafiles[1],
            media_keys)

        self.assertTrue(str(mediafiles[1]['id']) in mediafiles_txt2)
        self.assertTrue(mediafiles[1]['url'] in mediafiles_txt2)
        self.assertFalse(mediafiles[0]['url'] in mediafiles_txt2)
        self.assertTrue(mediafiles[1]['file_type'] in mediafiles_txt2)
        self.assertFalse('VideoFile' in mediafiles_txt2)
