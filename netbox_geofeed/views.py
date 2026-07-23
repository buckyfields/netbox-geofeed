import csv

from django.http import HttpResponse
from django.views import View

from netbox.views import generic

from . import filtersets, forms, tables
from .models import Geofeed

__all__ = (
    'GeofeedBulkDeleteView',
    'GeofeedDeleteView',
    'GeofeedEditView',
    'GeofeedFeedView',
    'GeofeedListView',
    'GeofeedView',
)


class GeofeedView(generic.ObjectView):
    queryset = Geofeed.objects.all()


class GeofeedListView(generic.ObjectListView):
    queryset = Geofeed.objects.all()
    table = tables.GeofeedTable
    filterset = filtersets.GeofeedFilterSet
    filterset_form = forms.GeofeedFilterForm


class GeofeedEditView(generic.ObjectEditView):
    queryset = Geofeed.objects.all()
    form = forms.GeofeedForm


class GeofeedDeleteView(generic.ObjectDeleteView):
    queryset = Geofeed.objects.all()


class GeofeedBulkDeleteView(generic.BulkDeleteView):
    queryset = Geofeed.objects.all()
    table = tables.GeofeedTable
    filterset = filtersets.GeofeedFilterSet


class GeofeedFeedView(View):
    """
    Publish every Geofeed entry as a single RFC 8805-compliant CSV feed.
    This view is intentionally left open to unauthenticated requests, since
    geofeeds are meant to be fetched by anonymous crawlers/resolvers. If
    your NetBox deployment enforces LOGIN_REQUIRED globally, exempt this
    path (see README.md).
    """

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response, lineterminator='\n')

        for geofeed in Geofeed.objects.all().order_by('id'):
            for cidr in geofeed.get_cidrs():
                writer.writerow([
                    cidr,
                    geofeed.country,
                    geofeed.region,
                    geofeed.city,
                    geofeed.postal_code,
                ])

        return response
