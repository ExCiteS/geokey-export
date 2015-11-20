from django.utils import timezone
from django.test import TestCase

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectF

from ..models import Export, post_save_project
from .model_factories import ExportFactory


class TemplateTagsTest(TestCase):

    def test_is_expired(self):
        export = Export(expiration=timezone.now())
        self.assertTrue(export.is_expired())

        export = Export()
        self.assertFalse(export.is_expired())

    def test_expire(self):
        export = ExportFactory.create(name='Test')
        self.assertFalse(export.is_expired())

        export.expire()
        self.assertTrue(export.is_expired())


class ProjectSaveTest(TestCase):

    def test_post_save_project_when_only_changing_status(self):
        project = ProjectF(**{'status': 'active'})
        ExportFactory.create(**{'project': project})

        project.status = 'pending'
        project.save

        post_save_project(Project, instance=project)
        self.assertEqual(
            Export.objects.filter(project=project).exists(),
            True
        )

    def test_post_save_project_when_deleting(self):
        project = ProjectF(**{'status': 'active'})
        ExportFactory.create(**{'project': project})

        project.status = 'deleted'
        project.save

        post_save_project(Project, instance=project)
        self.assertEqual(
            Export.objects.filter(project=project).exists(),
            False
        )
