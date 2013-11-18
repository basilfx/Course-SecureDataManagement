from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns("",
    url(r"^$", "phr_cli.views.index"),

    url(r"^select/$", "phr_cli.views.phr_select"),
    url(r"^connect/$", "phr_cli.views.phr_connect"),
    url(r"^create/$", "phr_cli.views.phr_create"),
    url(r"^import/$", "phr_cli.views.phr_import"),
)
