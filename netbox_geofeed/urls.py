from django.urls import path

from netbox.views.generic import ObjectChangeLogView

from . import views
from .models import Geofeed

app_name = 'netbox_geofeed'

urlpatterns = (
    path('geofeeds/', views.GeofeedListView.as_view(), name='geofeed_list'),
    path('geofeeds/add/', views.GeofeedEditView.as_view(), name='geofeed_add'),
    path('geofeeds/delete/', views.GeofeedBulkDeleteView.as_view(), name='geofeed_bulk_delete'),
    path('geofeeds/<int:pk>/', views.GeofeedView.as_view(), name='geofeed'),
    path('geofeeds/<int:pk>/edit/', views.GeofeedEditView.as_view(), name='geofeed_edit'),
    path('geofeeds/<int:pk>/delete/', views.GeofeedDeleteView.as_view(), name='geofeed_delete'),
    path(
        'geofeeds/<int:pk>/changelog/',
        ObjectChangeLogView.as_view(),
        name='geofeed_changelog',
        kwargs={'model': Geofeed},
    ),

    # Public RFC 8805 CSV feed, e.g. https://netbox.example.com/plugins/geofeed/geofeed.csv
    path('geofeed.csv', views.GeofeedFeedView.as_view(), name='geofeed_feed'),
)
