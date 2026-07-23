from netbox.plugins import PluginTemplateExtension

from .models import Geofeed


class BaseGeofeedPanel(PluginTemplateExtension):
    object_model = None  # e.g. 'prefix' or 'iprange'

    def right_page(self):
        obj = self.context['object']
        geofeed = Geofeed.objects.filter(
            assigned_object_type__model=self.object_model,
            assigned_object_id=obj.pk,
        ).first()
        return self.render('netbox_geofeed/inc/geofeed_panel.html', extra_context={
            'geofeed': geofeed,
        })


class PrefixGeofeedPanel(BaseGeofeedPanel):
    model = 'ipam.prefix'
    object_model = 'prefix'


class IPRangeGeofeedPanel(BaseGeofeedPanel):
    model = 'ipam.iprange'
    object_model = 'iprange'


template_extensions = [PrefixGeofeedPanel, IPRangeGeofeedPanel]
