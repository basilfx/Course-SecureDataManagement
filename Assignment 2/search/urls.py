from django.conf.urls import patterns, url

from search import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^logout/$', views.client_logout),

    url(r'^transactions/$', views.transactions),
    url(r'^login/$', views.login),
    url(r'^register/$', views.register),
    url(r'^createtransaction/$', views.createTransaction),
    url(r'^deletetransaction/$', views.deleteTransaction),

    url(r'^search/amount/(?P<amount>.+)$', views.search_amount),
    url(r'^search/date/(?P<date>.+)$', views.search_date),
    url(r'^search/amount/(?P<amount>.+)/date/(?P<date>.+)$', views.search_amount_date),

)