from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns("",
    url(r"^$", "phr_cli.views.index"),

    url(r"^select/$", "phr_cli.views.records_select"),
    url(r"^connect/$", "phr_cli.views.records_connect"),
    url(r"^create/$", "phr_cli.views.records_create"),
    url(r"^share/$", "phr_cli.views.records_share"),

    url(r"^encrypt/$", "phr_cli.views.record_items_create"),
    url(r"^decrypt/$", "phr_cli.views.record_items_list"),
    url(r"^decrypt/(?P<record_item_id>\d+)/$", "phr_cli.views.record_items_show"),

    url(r"^grant/$", "phr_cli.views.keys_grant"),
    url(r"^retrieve/$", "phr_cli.views.keys_retrieve"),

    url(r"^logout/$", "phr_cli.views.logout"),
)
