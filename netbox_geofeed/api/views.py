from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets
from ..models import Geofeed
from .serializers import GeofeedSerializer

__all__ = (
    'GeofeedViewSet',
)


class GeofeedViewSet(NetBoxModelViewSet):
    queryset = Geofeed.objects.all()
    serializer_class = GeofeedSerializer
    filterset_class = filtersets.GeofeedFilterSet
