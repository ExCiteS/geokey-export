"""Utils for geokey_export."""

from django.contrib.gis.geos import GEOSGeometry

from .base import comment_keys, keys_obs


def get_responses(obs_id, comment, length):
    """Get all the responses existing in a comment."""
    responses = []
    if comment['responses']:
        com = comment['responses']
        for rep in range(length):
            responses.append(get_info_comment(obs_id, com[rep], comment_keys))
            responses.extend(get_responses(
                obs_id,
                com[rep],
                len(com[rep]['responses']))
            )
    return responses


def get_fields(data):
    """Create list of all the existing fields for this observation."""
    keys_fields = ['geom', 'id', 'creator', 'creator_id', 'created_at', 'status']
    for i in range(len(data)):
        if data[i]['properties']:
            properties = data[i]['properties']
            fields = [prop_keys for prop_keys in properties.iterkeys()]
            for field in fields:
                if field not in keys_fields:
                    keys_fields.append(field)

    return keys_fields


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


def get_info_comment(obs_id, comment, keys):
    """Create list for each of the comment in the observation.

    Parameters:
        obs_id: int
            observation unique identifier number
        comment: dic
            contains all the values a comment
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
                if comment[key]:
                    comment_row.append(str(comment[key]))
                else:
                    comment_row.append('')
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
