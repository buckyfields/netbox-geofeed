from netbox.api.routers import NetBoxRouter

from . import views

router = NetBoxRouter()
router.register('geofeeds', views.GeofeedViewSet)

app_name = 'netbox_geofeed-api'
urlpatterns = router.urls
