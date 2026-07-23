import django_filters
from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from .models import Geofeed

__all__ = (
    'GeofeedFilterSet',
)


class GeofeedFilterSet(NetBoxModelFilterSet):
    country = django_filters.CharFilter(lookup_expr='iexact')
    region = django_filters.CharFilter(lookup_expr='iexact')
    city = django_filters.CharFilter(lookup_expr='icontains')
    postal_code = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Geofeed
        fields = ('id', 'country', 'region', 'city', 'postal_code')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(country__icontains=value) |
            Q(region__icontains=value) |
            Q(city__icontains=value) |
            Q(postal_code__icontains=value) |
            Q(comments__icontains=value)
        )
