# netbox-geofeed

A [NetBox](https://github.com/netbox-community/netbox) plugin (NetBox 4.x) for
publishing [RFC 8805](https://datatracker.ietf.org/doc/html/rfc8805)
self-published geofeeds — CSV files that map your address space to
geolocation data, which network operators, CDNs, and geolocation providers
can use to improve the accuracy of your IP geolocation.

## Features

- A `Geofeed` model that attaches country / region / city / postal code
  data to either an IPAM **Prefix** or an **IP Range**.
- A NetBox UI: list, add, edit, delete, changelog, and bulk delete views
  under **Plugins → Geofeeds**.
- A read-only panel injected onto the Prefix and IP Range detail pages
  showing (or offering to add) the geofeed entry for that object.
- A full REST API (`/api/plugins/geofeed/geofeeds/`).
- Global search integration.
- A public, unauthenticated CSV export at `/plugins/geofeed/geofeed.csv`
  that renders every entry as an RFC 8805-compliant feed. IP ranges are
  automatically decomposed into the minimal set of CIDR blocks the RFC
  requires.

## Installation

These steps assume a standard NetBox installation using a Python virtual
environment, per the [NetBox plugin docs](https://netboxlabs.com/docs/netbox/en/stable/plugins/).

1. Copy the `netbox_geofeed/` package into your NetBox plugins directory
   (or install it as an editable package):

   ```bash
   source /opt/netbox/venv/bin/activate
   pip install -e /path/to/netbox-geofeed
   ```

2. Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`:

   ```python
   PLUGINS = [
       'netbox_geofeed',
   ]
   ```

3. Generate and apply the database migration. This plugin intentionally
   ships without a pre-built migration, since the exact migration graph
   (dependency on the `extras` app's `Tag` model) differs between NetBox
   point releases — generating it against *your* installed version avoids
   a mismatch:

   ```bash
   cd /opt/netbox/netbox
   python3 manage.py makemigrations netbox_geofeed
   python3 manage.py migrate netbox_geofeed
   ```

4. Collect static files and restart NetBox:

   ```bash
   python3 manage.py collectstatic --no-input
   sudo systemctl restart netbox netbox-rq
   ```

## Usage

Go to **Plugins → Geofeeds** to add an entry, choosing either a Prefix or
an IP Range to attach it to, plus a country code and optional region,
city, and postal code. The entry then also shows up as a panel on that
Prefix's or IP Range's own detail page.

Fetch the full feed at:

```
https://<your-netbox-host>/plugins/geofeed/geofeed.csv
```

### Publishing the feed at a well-known location

RFC 8805 recommends referencing your geofeed from WHOIS/RDAP remarks, and
many consumers also check `https://<domain>/.well-known/geofeed`. Since
that well-known path is unrelated to NetBox's own URL space, redirect it
at your reverse proxy, e.g. in nginx:

```nginx
location = /.well-known/geofeed {
    return 302 https://netbox.example.com/plugins/geofeed/geofeed.csv;
}
```

### If your NetBox instance enforces `LOGIN_REQUIRED`

The CSV feed view has no `@login_required` decorator, but NetBox's global
`LOGIN_REQUIRED` middleware setting, if enabled, will still redirect
anonymous requests to the login page for any URL by default. If you rely
on that setting, allow anonymous access to `/plugins/geofeed/geofeed.csv`
specifically (via your reverse proxy, or NetBox's exempt-path settings),
since geofeeds must be fetchable by unauthenticated crawlers to be useful.

## REST API

```
GET  /api/plugins/geofeed/geofeeds/
POST /api/plugins/geofeed/geofeeds/
GET  /api/plugins/geofeed/geofeeds/<id>/
```

Example creation payload assigning a geofeed to a prefix:

```json
{
  "assigned_object_type": "ipam.prefix",
  "assigned_object_id": 42,
  "country": "US",
  "region": "US-CA",
  "city": "San Francisco",
  "postal_code": "94105"
}
```

## Compatibility

Developed against NetBox 4.x. Built-in NetBox APIs and template blocks
occasionally shift between minor releases (e.g. plugin `fieldsets` syntax,
`PluginTemplateExtension` hook names); if something doesn't load after
install, check your NetBox version's plugin development docs for the
current form of the API used in `forms.py` / `template_content.py`.
