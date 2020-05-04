from django.conf.urls import include, url

from phr_cli import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r"^$", views.index),

    url(r"^select/$", views.records_select),
    url(r"^connect/$", views.records_connect),
    url(r"^create/$", views.records_create),
    url(r"^share/$", views.records_share),

    url(r"^encrypt/$", views.record_items_create),
    url(r"^decrypt/$", views.record_items_list),
    url(r"^decrypt/(?P<record_item_id>\d+)/$", views.record_items_show),

    url(r"^grant/$", views.keys_grant),
    url(r"^retrieve/$", views.keys_retrieve),

    url(r"^logout/$", views.logout),
]
