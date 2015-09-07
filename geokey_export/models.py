from django.utils import timezone

from django.db import models
from django.conf import settings


class Export(models.Model):

    """
    Stores a single export.
    """
    name = models.CharField(max_length=100)
    project = models.ForeignKey('projects.Project')
    category = models.ForeignKey('categories.Category', null=True, blank=True)
    isoneoff = models.BooleanField(default=False)
    expiration = models.DateTimeField(null=True)
    urlhash = models.CharField(max_length=40)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)

    def is_expired(self):
        if self.expiration:
            return self.expiration < timezone.now()

        return False

    def expire(self):
        self.expiration = timezone.now()
        self.save()
