from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from utilities.api import get_serializer_for_model

from ..models import Geofeed

__all__ = (
    'GeofeedSerializer',
)


class GeofeedSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_geofeed-api:geofeed-detail')
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(model__in=['prefix', 'iprange']),
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Geofeed
        fields = (
            'id', 'url', 'display', 'assigned_object_type', 'assigned_object_id', 'assigned_object',
            'country', 'region', 'city', 'postal_code', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'country', 'region', 'city', 'postal_code')

    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {'request': self.context.get('request')}
        return serializer(obj.assigned_object, nested=True, context=context).data
