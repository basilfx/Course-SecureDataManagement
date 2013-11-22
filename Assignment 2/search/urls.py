from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', 'search.views.client_logout'),

    url(r'^$', 'search.views.index'),

    url(r'^transactions/$', 'search.views.transactions'),
    url(r'^login/$', 'search.views.do_login'),
    url(r'^register/$', 'search.views.register'),
    url(r'^createtransaction/$', 'search.views.createTransaction'),
    url(r'^deletetransaction/$', 'search.views.deleteTransaction'),
    url(r'^search/$', 'search.views.search_amount_date'),

)