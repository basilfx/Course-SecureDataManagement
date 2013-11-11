from django.conf.urls import patterns, url

from search import views

urlpatterns = patterns('',
    url(r'^$', views.transaction_index),
    url(r'^transactions/$', views.transaction_index),
    url(r'^transactions/new/$', views.transaction_new),
    url(r'^transactions/(?P<transaction_id>\d+)/edit/$', views.transaction_edit),
    url(r'^transactions/(?P<transaction_id>\d+)/$', views.transaction_show),
    url(r'^transactions/$', views.transaction_index),
    url(r'^login/$', views.client_login),
    url(r'^authenticate/$', views.client_authenticate),
    url(r'^register/$', views.client_register),
    url(r'^client/$', views.client_index),
    url(r'^logout/$', views.client_logout),
    url(r'^search/(?P<query>.+)$', views.transaction_search),
)