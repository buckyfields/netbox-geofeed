from netbox.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_geofeed:geofeed_list',
        link_text='Geofeeds',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_geofeed:geofeed_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
            ),
        ),
    ),
)
