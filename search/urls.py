from django.conf.urls import patterns, url

from search import views

urlpatterns = patterns('',
	url(r'^transaction/new/$', views.transaction_new),
	url(r'^test/$', views.test),
	url(r'^transaction/(?P<transaction_id>\d+)/edit/$', views.transaction_edit),
	url(r'^transaction/(?P<transaction_id>\d+)/$', views.transaction_show),
    url(r'^transaction/$', views.transaction_index),
    url(r'^client/$', views.client_index),
)