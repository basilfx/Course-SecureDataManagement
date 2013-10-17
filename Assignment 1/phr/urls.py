from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('phr.my_app.urls')),
)

# Media files in development mode
if settings.DEBUG:
    urlpatterns += patterns("",
        (r"^%s(?P<path>.*)$" % (settings.MEDIA_URL[1:]), "django.views.static.serve", {"document_root": settings.MEDIA_ROOT}),
    )

# Error handlers
handler403 = "phr.views.handler403"
handler404 = "phr.views.handler404"
handler500 = "phr.views.handler500"