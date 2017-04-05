"""GeoJSON renderer."""

from rest_framework.renderers import BaseRenderer
from django.contrib.gis.geos import GEOSGeometry


class CSVRenderer(BaseRenderer):
    """Renderes serialised Contributions into text to be exported as csv."""
    media_type = 'text/csv'
    format = 'csv'

    def render_mediafiles(self, data):
        """Create the csv file all the comments for all the contributions."""
        media_keys = ['file_id', 'file_type', 'contribution_id', 'creator',
            'creator_id', 'created_at', 'url']
        mediafiles_csv = [';'.join(media_keys)]
        for i in range(len(data)):
            obs_id = data[i]['id']
            if data[i]['media']:
                media = data[i]['media']
                for m in media:
                    mediafiles_csv.append(get_mediafiles(obs_id, m, media_keys))
                    print "media id", m['id']
                    print "media url", m['url']

        return '\n'.join(mediafiles_csv)

    def render_comments(self, data):
        """Create the csv file all the comments for all the contributions."""
        comment_keys = ['comment_id', 'contribution_id', 'creator', 'creator_id',
            'created_at', 'respondsto', 'text']
        comments_csv = [';'.join(comment_keys)]
        for i in range(len(data)):
            obs_id = data[i]['id']
            for cm in data[i]['comments']:
                comments_csv.append(get_info_comments(obs_id, cm, comment_keys))
                responses = cm['responses']
                if responses != []:
                    for rp in range(len(responses)):
                        comments_csv.append(get_info_comments(
                            obs_id,
                            responses[rp],
                            comment_keys))

        return '\n'.join(comments_csv)

    def render_contribution(self, data):
        """Create the csv file all the contributions."""
        keys = ['geom', 'id', 'creator', 'creator_id', 'created_at', 'status']
        prop_keys = get_fields(data)
        keys.extend(prop_keys)
        all_csv_rows = [';'.join(keys)]
        for i in range(len(data)):
            all_csv_rows.append(create_observation_row(data[i], keys))

        return '\n'.join(all_csv_rows)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render `data` into serialized html text."""
        rendered = self.render_contribution(data)

        return rendered


def get_fields(data):
    """Create list of all the existing fields for this observation."""
    keys = []
    for i in range(len(data)):
        properties = data[i]['properties']
        fields = [prop_keys for prop_keys in properties.iterkeys()]
        for field in fields:
            if field not in keys:
                keys.append(field)
    return keys


def get_mediafiles(obs_id, mediafile, keys):
    """Create list for each of the comment in the observation.

    Parameters:
        obs_id: int
            observation unique identifier number
        mediafile: dic
            contains all the observation for a category
        keys: list
            key which represent the field values for the csv file

    returns:
        csw_row: str
            media files values contactenated with ';'
    """

    if mediafile:
        mediafile_row = []
        for key in keys:
            if key == 'file_id':
                mediafile_row.append(str(mediafile['id']))
            if key == 'contribution_id':
                mediafile_row.append(str(obs_id))
            if key == 'creator':
                mediafile_row.append(str(mediafile[key]['display_name']))
            if key == 'creator_id':
                mediafile_row.append(str(mediafile['creator']['id']))
            if key == 'url':
                mediafile_row.append(str(mediafile[key]))
            if key == 'created_at':
                mediafile_row.append(str(mediafile[key]))
            if key == 'file_type':
                mediafile_row.append(str(mediafile[key]))

        return ';'.join(mediafile_row)


def get_info_comments(obs_id, comment, keys):
    """Create list for each of the comment in the observation.

    Parameters:
        obs_id: int
            observation unique identifier number
        comment: dic
            contains all the observation for a category
        keys: list
            key which represent the field values for the csv file

    returns:
        csw_row: list
            observation values
    """
    if comment:
        comment_row = []
        for key in keys:
            if key == 'comment_id':
                comment_row.append(str(comment['id']))
            if key == 'contribution_id':
                comment_row.append(str(obs_id))
            if key == 'creator':
                comment_row.append(str(comment[key]['display_name']))
            if key == 'creator_id':
                comment_row.append(str(comment['creator']['id']))
            if key == 'text':
                comment_row.append(str(comment[key]))
            if key == 'created_at':
                comment_row.append(str(comment[key]))
            if key == 'respondsto':
                comment_row.append(str(comment[key]))
        comment_row = ';'.join(comment_row)
        return comment_row


def create_observation_row(data, keys):
    """Create list of the observation values specified on keys.

    Parameters:
        data: serilized list
            contains all the observation for a category
        keys: list
            key which represent the field values for the csv file

    returns:
        csw_row: string
            string with observation values ';' delimiter
    """
    csv_row = []
    for key in keys:
        if key == 'geom':
            geom = GEOSGeometry(data['location']['geometry'])
            csv_row.append(geom.wkt)
        elif key == 'status':
            csv_row.append(str(data['meta']['status']))
        elif key == 'creator':
            csv_row.append(str(data['meta']['creator']['display_name']))
        elif key == 'creator_id':
            csv_row .append(str(data['meta']['creator']['id']))
        elif key == 'created_at':
            csv_row.append(str(data['meta']['created_at']))
        elif key == 'id':
            csv_row.append(str(data['id']))
        else:
            try:
                csv_row.append(str(data['properties'][key]))
            except:
                csv_row.append('')
    csv_row = ';'.join(csv_row)
    return csv_row
