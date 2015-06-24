import factory

from geokey.projects.tests.model_factories import ProjectF
from geokey.users.tests.model_factories import UserF

from ..models import Export


class ExportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Export

    name = factory.Sequence(lambda n: 'Export %d' % n)
    project = factory.SubFactory(ProjectF)
    urlhash = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    creator = factory.SubFactory(UserF)
