#

from django.urls import re_path, include, path

from . import auth as custom_auth
from . import views

urlpatterns = [

    re_path(r'^coup/$', views.coup, name='coup'),
    # re_path(r'^coup/(?P<o_id>[0-9]+)/$', views.coup, name='coup'),
    re_path(r'^locker/$', views.locker, name='locker'),
    # re_path(r'^locker/(?P<o_id>[0-9]+)/$', views.locker, name='locker'),
    re_path(r'^pwcont/$', views.pwcont, name='pwcont'),
    # re_path(r'^pwcont/(?P<o_id>[0-9]+)/$', views.pwcont, name='pwcont'),
    re_path(r'^polyline/$', views.polyline, name='polyline'),
    re_path(r'^polyline/(?P<o_id>[0-9]+)/$', views.polyline, name='polyline'),

    re_path(r'^coup/(?P<o_id>[0-9]+)/links/$', views.coup_links, name='coup_links'),

    re_path(r'^coup/(?P<o_id>[0-9]+)/paint/$', views.coup_paint, name='coup_paint'),

    re_path(r'^coup/(?P<o_id>[0-9]+)/paintext/(?P<cab_l>[0-9,-]+)/$', views.coup_paint_ext, name='coup_paint_ext'),

    re_path(r'^show_hop/(?P<o_id>[0-9]+)/$', views.show_hop, name='show_hop'),

    # path('api-token-auth/', t_views.obtain_auth_token)
    path('api-token-auth/', custom_auth.auth_token)

]
