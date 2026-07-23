import django_tables2 as tables

from netbox.tables import NetBoxTable, columns

from .models import Geofeed

__all__ = (
    'GeofeedTable',
)


class GeofeedTable(NetBoxTable):
    assigned_object_type = columns.ContentTypeColumn(
        verbose_name='Object Type',
    )
    assigned_object = tables.Column(
        linkify=True,
        verbose_name='Assigned Object',
        orderable=False,
    )
    country = tables.Column()
    region = tables.Column()
    city = tables.Column()
    postal_code = tables.Column()
    tags = columns.TagColumn(
        url_name='plugins:netbox_geofeed:geofeed_list',
    )

    class Meta(NetBoxTable.Meta):
        model = Geofeed
        fields = (
            'pk', 'id', 'assigned_object_type', 'assigned_object', 'country', 'region', 'city',
            'postal_code', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'assigned_object_type', 'assigned_object', 'country', 'region', 'city', 'postal_code',
        )
