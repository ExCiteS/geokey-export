"""GeoJSON renderer."""

from rest_framework.renderers import BaseRenderer
from .base import media_keys, comment_keys
from .utils import (
    get_responses,
    get_fields,
    get_mediafiles,
    get_info_comment,
    create_observation_row
)


class CSVRenderer(BaseRenderer):
    """Renderes serialised Contributions into text to be exported as csv."""
    media_type = 'text/csv'
    format = 'csv'

    def render_mediafiles(self, data):
        """Create the csv file all the comments for all the contributions."""
        mediafiles_csv = [';'.join(media_keys)]
        for i in range(len(data)):
            obs_id = data[i]['id']
            if data[i]['media']:
                media = data[i]['media']
                for m in media:
                    mediafiles_csv.append(get_mediafiles(obs_id, m, media_keys))
        return '\n'.join(mediafiles_csv)

    def render_comments(self, data):
        """Create the csv file all the comments for all the contributions."""
        comments_csv = [';'.join(comment_keys)]
        for i in range(len(data)):
            obs_id = data[i]['id']
            for cm in data[i]['comments']:
                comments_csv.append(get_info_comment(obs_id, cm, comment_keys))
                responses = cm['responses']
                comments_csv.extend(get_responses(obs_id, cm, len(responses)))

        return '\n'.join(comments_csv)

    def render_contribution(self, data):
        """Create the csv file all the contributions."""
        keys_obs = get_fields(data)
        all_csv_rows = [';'.join(keys_obs)]
        for i in range(len(data)):
            all_csv_rows.append(create_observation_row(data[i], keys_obs))

        return '\n'.join(all_csv_rows)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Render `data` into serialized html text."""
        rendered = self.render_contribution(data)

        return rendered
