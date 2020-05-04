from django.conf.urls import include, url
from django.contrib import admin

from search import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name="search-views-index"),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', views.client_logout),
    url(r'^client-login/$', views.client_login),
    url(r'^consultant-login/$', views.consultant_login),
    url(r'^client-register/$', views.client_register),
    url(r'^consultant-register/$', views.consultant_register),


    url(r'^consultants/$', views.consultants),
    url(r'^clientlist/$', views.client_list),

    url(r'^transactions/$', views.transactions),
    url(r'^transactions/create/$', views.transactions_create),
    url(r'^transactions/delete/$', views.transactions_delete),

    url(r'^search/$', views.search_amount_date),
]