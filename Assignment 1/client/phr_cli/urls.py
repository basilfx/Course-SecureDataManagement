from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns("",
    url(r"^$", "phr_cli.views.index"),

    url(r"^select/$", "phr_cli.views.select"),
    url(r"^connect/$", "phr_cli.views.connect"),
    url(r"^create/$", "phr_cli.views.create"),

    url(r"^encrypt/$", "phr_cli.views.encrypt"),
    url(r"^decrypt/(?P<record_item_id>\d+)/$", "phr_cli.views.decrypt"),

    url(r"^share/$", "phr_cli.views.share"),
    url(r"^grant/$", "phr_cli.views.grant"),
    url(r"^retrieve/$", "phr_cli.views.retrieve"),

    url(r"^logout/$", "phr_cli.views.logout"),
)
