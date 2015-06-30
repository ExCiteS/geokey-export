import datetime, json, random, string

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages

from rest_framework.views import APIView

from braces.views import LoginRequiredMixin

from geokey.categories.models import Category
from geokey.contributions.serializers import ContributionSerializer
from geokey.contributions.renderer.geojson import GeoJsonRenderer
from geokey.contributions.renderer.kml import KmlRenderer
from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.projects.models import Project

from .models import Export

class IndexPage(LoginRequiredMixin, TemplateView):
    template_name = 'export_index.html'

    def get_context_data(self, *args, **kwargs):
        exports = Export.objects.all()

        return super(IndexPage, self).get_context_data(
            name='GeoKey Export',
            exports=exports,
            *args,
            **kwargs
        )


class ExportCreate(LoginRequiredMixin, TemplateView):
    template_name = 'export_create.html'

    def get_context_data(self, *args, **kwargs):
        projects = Project.objects.get_list(self.request.user)
        first_project_id = None
        for project in projects:
            first_project_id = project.id
            break

        if first_project_id is not None:
            categories = Category.objects.get_list(self.request.user, first_project_id)

        return super(ExportCreate, self).get_context_data(
            name='GeoKey Export',
            projects=projects,
            categories=categories,
            *args,
            **kwargs
        )

    def post(self, request):
        name = self.request.POST.get('exportName')

        project_id = self.request.POST.get('exportProject')
        project = Project.objects.get_single(self.request.user, project_id)

        category_id = self.request.POST.get('exportCategory')
        category = Category.objects.get_single(self.request.user, project_id, category_id)

        #filter = self.request.POST.get('filter')

        expiration_val = self.request.POST.get('exportExpiration')
        isoneoff = False
        expiration = None
        if expiration_val == "one_off":
            isoneoff = True
        elif expiration_val == "one_week":
            expiration = datetime.datetime.now() + datetime.timedelta(days=7)

        creator = self.request.user

        urlhash = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(40)])
        export_check = Export.objects.filter(urlhash=urlhash).exists()
        while export_check:
            urlhash = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(40)])
            export_check = Export.objects.filter(urlhash=urlhash).exists()

        export = Export.objects.create(
            name=name,
            project=project,
            category=category,
            # filter=filter,
            isoneoff=isoneoff,
            expiration=expiration,
            urlhash=urlhash,
            creator=creator
        )

        return redirect('geokey_export:export_overview', export_id=export.id)

class ExportCreateUpdateCategories(LoginRequiredMixin, APIView):
    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        categories = Category.objects.get_list(self.request.user, project_id)
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.name

        return HttpResponse(json.dumps(categories_dict))

class ExportObjectMixin(object):
    def get_context_data(self, user, export_id, **kwargs):
        export = Export.objects.get(pk=export_id)
        if export.creator != user:
            return {
                'error_description': 'You must be the creator of the export.',
                'error': 'Permission denied.'
            }
        else:
            return super(ExportObjectMixin, self).get_context_data(
                export=export, **kwargs)

# Had to add this method in order to deal with ExportOverview not passing user,
# but ExportDelete does and requires it. Need to sort soon...
class ExportObjectMixin1(object):
    def get_context_data(self, export_id, **kwargs):
        export = Export.objects.get(pk=export_id)
        user = self.request.user
        if export.creator != user:
            return {
                'error_description': 'You must be the creator of the export.',
                'error': 'Permission denied.'
            }
        else:
            return super(ExportObjectMixin1, self).get_context_data(
                export=export, **kwargs)


class ExportOverview(LoginRequiredMixin, ExportObjectMixin1, TemplateView):
    template_name = 'export_overview.html'


class ExportDelete(LoginRequiredMixin, ExportObjectMixin, TemplateView):
    template_name = 'base.html'

    def get(self, request, export_id):
        context = self.get_context_data(request.user, export_id)
        export = context.pop('export', None)

        if export is not None:
            export.delete()

            messages.success(self.request, "The export has been deleted.")
            return redirect('geokey_export:index')

        return self.render_to_response(context)


class ExportToRenderer(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    def get_context_data(self, urlhash, **kwargs):
        urlhash = urlhash

        return super(ExportToRenderer, self).get_context_data(
            urlhash=urlhash, **kwargs)

    def get(self, request, urlhash, format=None):
        export = Export.objects.get(urlhash=urlhash)
        contributions = export.project.get_all_contributions(export.creator).filter(category=export.category)
        # perhaps we want to alert the user when there are no contributions?

        serializer = ContributionSerializer(
            contributions,
            many=True,
            context={'user': export.creator, 'project': export.project}
        )

        if format == 'json':
            renderer = GeoJsonRenderer()
        elif format == 'kml':
            renderer = KmlRenderer()
        else:
            renderer = None

        if renderer:
            content = renderer.render(serializer.data)
        else:
            pass
            # return response that format is not supported

        return HttpResponse(content, content_type="text/plain")
