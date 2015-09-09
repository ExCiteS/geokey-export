import datetime
import json
import string
import random

from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.views import APIView

from braces.views import LoginRequiredMixin

from geokey import version
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
        exports = Export.objects.filter(creator=self.request.user)

        return super(IndexPage, self).get_context_data(
            exports=exports,
            *args,
            **kwargs
        )


class ExportExpiryMixin(object):
    def get_expiry(self, expiration_val):
        isoneoff = False
        expiration = None
        if expiration_val == "one_off":
            isoneoff = True
        elif expiration_val == "one_week":
            expiration = timezone.now() + datetime.timedelta(days=7)

        return isoneoff, expiration


class ExportCreate(LoginRequiredMixin, ExportExpiryMixin, TemplateView):
    template_name = 'export_create.html'

    def get_context_data(self, *args, **kwargs):
        projects = Project.objects.get_list(self.request.user)

        return super(ExportCreate, self).get_context_data(
            projects=projects,
            *args,
            **kwargs
        )

    def get_hash(self):
        export_check = True

        while export_check:
            urlhash = ''.join([
                random.choice(string.ascii_letters + string.digits)
                for n in xrange(40)
            ])
            export_check = Export.objects.filter(urlhash=urlhash).exists()

        return urlhash

    def post(self, request):
        name = self.request.POST.get('exportName')

        project_id = self.request.POST.get('exportProject')
        project = Project.objects.get_single(self.request.user, project_id)

        category_id = self.request.POST.get('exportCategory')
        category = Category.objects.get_single(
            self.request.user,
            project_id,
            category_id
        )

        isoneoff, expiration = self.get_expiry(
            self.request.POST.get('exportExpiration')
        )

        creator = self.request.user
        urlhash = self.get_hash()

        export = Export.objects.create(
            name=name,
            project=project,
            category=category,
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

    def get_context_data(self, export_id, **kwargs):
        try:
            export = Export.objects.get(pk=export_id)

            if export.creator != self.request.user:
                return {
                    'error_description': 'You must be creator of the export.',
                    'error': 'Permission denied.'
                }
            else:
                return super(ExportObjectMixin, self).get_context_data(
                    export=export,
                    **kwargs
                )
        except Export.DoesNotExist:
            return {
                'error_description': 'Export not found.',
                'error': 'Not found.'
            }


class ExportOverview(LoginRequiredMixin, ExportExpiryMixin, ExportObjectMixin,
                     TemplateView):
    template_name = 'export_overview.html'

    def post(self, request, export_id):
        context = self.get_context_data(export_id)
        if context.get('export'):
            export = context['export']

            isoneoff, expiration = self.get_expiry(
                self.request.POST.get('exportExpiration')
            )
            export.isoneoff = isoneoff
            export.expiration = expiration
            export.save()

        return self.render_to_response(context)


class ExportDelete(LoginRequiredMixin, ExportObjectMixin, TemplateView):
    template_name = 'base.html'

    def get(self, request, export_id):
        context = self.get_context_data(export_id)
        export = context.pop('export', None)

        if export is not None:
            export.delete()

            messages.success(self.request, "The export has been deleted.")
            return redirect('geokey_export:index')

        return self.render_to_response(context)


class ExportToRenderer(View):

    def get_context(self, request, urlhash):
        context = {
            'PLATFORM_NAME': get_current_site(self.request).name,
            'user': request.user,
            'GEOKEY_VERSION': version.get_version()
        }

        error_context = context.copy()
        error_context.update({
            'error_description': 'The export was not found in the database.',
            'error': 'Not found.'
        })

        try:
            export = Export.objects.get(urlhash=urlhash)
        except Export.DoesNotExist:
            context = error_context
        else:
            if export.is_expired():
                context = error_context
            else:
                context['export'] = export

        return context

    def get(self, request, urlhash, format=None):
        context = self.get_context(request, urlhash)
        export = context.get('export')

        if export and format:
            content_type = 'text/plain'

            if format == 'json':
                renderer = GeoJsonRenderer()
            elif format == 'kml':
                renderer = KmlRenderer()

            contributions = export.project.get_all_contributions(
                export.creator).filter(category=export.category)

            serializer = ContributionSerializer(
                contributions,
                many=True,
                context={'user': export.creator, 'project': export.project}
            )
            content = renderer.render(serializer.data)

            if export.isoneoff:
                export.expire()
        else:
            content = render_to_string('export_access.html', context)
            content_type = 'text/html'

        return HttpResponse(content, content_type=content_type)
