"""Runtime compatibility smoke test for NetBox Community v4.6.5."""

import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netbox.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from ipam.models import IPRange, Prefix
from netbox.registry import registry

from netbox_geofeed.models import Geofeed
from netbox_geofeed.template_content import IPRangeGeofeedPanel, PrefixGeofeedPanel


def assert_status(client, url, expected=200):
    response = client.get(url)
    assert response.status_code == expected, (
        f"GET {url} returned {response.status_code}: "
        f"{response.content[:1000]!r}"
    )
    return response


def assert_template_extension_scope():
    """Ensure geofeed panels are registered only for their intended IPAM models."""
    extensions = registry["plugins"]["template_extensions"]
    global_extensions = extensions.get(None, [])
    prefix_extensions = extensions.get("ipam.prefix", [])
    ip_range_extensions = extensions.get("ipam.iprange", [])

    assert PrefixGeofeedPanel in prefix_extensions, (
        "PrefixGeofeedPanel is not registered for ipam.prefix. "
        "NetBox 4.6.5 expects PluginTemplateExtension.models (plural) to be a list."
    )
    assert IPRangeGeofeedPanel in ip_range_extensions, (
        "IPRangeGeofeedPanel is not registered for ipam.iprange. "
        "NetBox 4.6.5 expects PluginTemplateExtension.models (plural) to be a list."
    )
    assert PrefixGeofeedPanel not in global_extensions, (
        "PrefixGeofeedPanel was registered globally instead of only for ipam.prefix."
    )
    assert IPRangeGeofeedPanel not in global_extensions, (
        "IPRangeGeofeedPanel was registered globally instead of only for ipam.iprange."
    )


def main():
    results = {}

    assert_template_extension_scope()
    results["template_extension_registration"] = "passed"

    prefix = Prefix(prefix="192.0.2.0/24", description="Geofeed compatibility test")
    prefix.full_clean()
    prefix.save()

    ip_range = IPRange(
        start_address="198.51.100.1/32",
        end_address="198.51.100.6/32",
        description="Geofeed compatibility test",
    )
    ip_range.full_clean()
    ip_range.save()

    prefix_geofeed = Geofeed(
        assigned_object=prefix,
        country="us",
        region="us-va",
        city="Ashburn",
        postal_code="20147",
    )
    prefix_geofeed.full_clean()
    prefix_geofeed.save()

    range_geofeed = Geofeed(
        assigned_object=ip_range,
        country="US",
        region="US-VA",
        city="Leesburg",
        postal_code="20175",
    )
    range_geofeed.full_clean()
    range_geofeed.save()

    assert prefix_geofeed.country == "US"
    assert prefix_geofeed.region == "US-VA"
    assert prefix_geofeed.get_cidrs() == ["192.0.2.0/24"]
    assert range_geofeed.get_cidrs() == [
        "198.51.100.1/32",
        "198.51.100.2/31",
        "198.51.100.4/31",
        "198.51.100.6/32",
    ]
    results["model_and_cidr_conversion"] = "passed"

    anonymous_client = Client()
    csv_url = reverse("plugins:netbox_geofeed:geofeed_feed")
    csv_response = assert_status(anonymous_client, csv_url)
    csv_body = csv_response.content.decode("utf-8")
    expected_rows = {
        "192.0.2.0/24,US,US-VA,Ashburn,20147",
        "198.51.100.1/32,US,US-VA,Leesburg,20175",
        "198.51.100.2/31,US,US-VA,Leesburg,20175",
        "198.51.100.4/31,US,US-VA,Leesburg,20175",
        "198.51.100.6/32,US,US-VA,Leesburg,20175",
    }
    assert set(csv_body.strip().splitlines()) == expected_rows, csv_body
    assert csv_response["Content-Type"].startswith("text/csv")
    results["anonymous_csv_export"] = "passed"

    user_model = get_user_model()
    admin = user_model.objects.create_superuser(
        username="geofeed-admin",
        email="geofeed-admin@example.com",
        password="NetBox-Geofeed-Test-Password-123!",
    )
    authenticated_client = Client()
    authenticated_client.force_login(admin)

    ui_urls = [
        reverse("plugins:netbox_geofeed:geofeed_list"),
        reverse("plugins:netbox_geofeed:geofeed", args=[prefix_geofeed.pk]),
        reverse("plugins:netbox_geofeed:geofeed_add"),
        prefix.get_absolute_url(),
        ip_range.get_absolute_url(),
    ]
    for url in ui_urls:
        assert_status(authenticated_client, url)
    results["ui_and_template_extensions"] = "passed"

    api_url = reverse("plugins-api:netbox_geofeed-api:geofeed-list")
    api_response = assert_status(authenticated_client, api_url)
    api_payload = api_response.json()
    assert api_payload["count"] == 2, json.dumps(api_payload, indent=2)
    assert len(api_payload["results"]) == 2
    results["rest_api"] = "passed"

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
