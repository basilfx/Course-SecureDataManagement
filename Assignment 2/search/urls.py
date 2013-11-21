from django.conf.urls import patterns, url

from search import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^logout/$', views.client_logout),

    url(r'^transactions/$', views.transactions),
    url(r'^login/$', views.do_login),
    url(r'^clientregister/$', views.client_register),
    url(r'^consultantregister/$', views.consultant_register),
    url(r'^createtransaction/$', views.createTransaction),
    url(r'^deletetransaction/$', views.deleteTransaction),
    url(r'^search/$', views.search_amount_date),

)