from netbox.plugins import PluginConfig


class GeofeedConfig(PluginConfig):
    name = 'netbox_geofeed'
    verbose_name = 'Geofeed'
    description = 'Publish RFC 8805 self-published geolocation feeds for IPAM prefixes and IP ranges.'
    version = '1.0.0'
    author = 'Your Name'
    author_email = 'you@example.com'
    base_url = 'geofeed'
    min_version = '4.0.0'
    max_version = '4.99'

    # Set to True to require an authenticated NetBox session to view the
    # editable Geofeed objects in the UI. This has no effect on the public
    # CSV feed endpoint, which is always served without authentication
    # (geofeeds are meant to be fetched by anonymous crawlers per RFC 8805).
    default_settings = {
        'require_authentication': False,
    }


config = GeofeedConfig
