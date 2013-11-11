from django.conf.urls import patterns, include, url
from django.conf import settings

from jsonrpc import jsonrpc_site

from phr import api


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns("",
  url(r"^browse/", "jsonrpc.views.browse", name="jsonrpc_browser"),
  url(r"^$", jsonrpc_site.dispatch, name="jsonrpc_mountpoint"),
)

# Media files in development mode
if settings.DEBUG:
    urlpatterns += patterns("",
        (r"^%s(?P<path>.*)$" % (settings.MEDIA_URL[1:]), "django.views.static.serve", {"document_root": settings.MEDIA_ROOT}),
    )