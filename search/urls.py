from django.conf.urls import patterns, url

from search import views

urlpatterns = patterns('',
	url(r'^transaction_new/$', views.transaction_new),
	url(r'^test/$', views.test),
	url(r'^(?P<transaction_id>\d+)/edit/$', views.transaction_edit),
	url(r'^(?P<transaction_id>\d+)/$', views.transaction_show),
    url(r'^$', views.transaction_index),
)