from netbox.search import SearchIndex, register_search

from .models import Geofeed


@register_search
class GeofeedIndex(SearchIndex):
    model = Geofeed
    fields = (
        ('country', 100),
        ('region', 100),
        ('city', 100),
        ('postal_code', 100),
        ('comments', 5000),
    )
