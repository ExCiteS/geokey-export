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
    #filter = ?
