import factory

from geokey.projects.tests.model_factories import ProjectFactory
from geokey.users.tests.model_factories import UserFactory

from ..models import Export


class ExportFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Export

    name = factory.Sequence(lambda n: 'Export %d' % n)
    project = factory.SubFactory(ProjectFactory)
    urlhash = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    creator = factory.SubFactory(UserFactory)
