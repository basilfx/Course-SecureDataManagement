from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'search.views.index'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', 'search.views.client_logout'),
    url(r'^login/$', 'search.views.client_login'),
    url(r'^register/$', 'search.views.client_register'),


    url(r'^consultants/$', 'search.views.consultants'),
    url(r'^clientlist/$', 'search.views.client_list'),

    url(r'^transactions/$', 'search.views.transactions'),
    url(r'^transactions/create/$', 'search.views.transactions_create'),
    url(r'^transactions/delete/$', 'search.views.transactions_delete'),

    url(r'^search/$', 'search.views.search_amount_date'),
)