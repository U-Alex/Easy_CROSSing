#

from django.urls import re_path, include, path
from rest_framework import routers
from rest_framework.authtoken import views as t_views

from . import views

# router = routers.DefaultRouter()
# router.register(r'coup', views.CoupViewSet, basename='coup')
# router.register(r'groups', views.GroupViewSet)


urlpatterns = [

    # re_path(r'^login/$', views.login, name='login'),
    re_path(r'^coup/$', views.coup, name='coup'),
    re_path(r'^coup/(?P<o_id>[0-9]+)/$', views.coup, name='coup'),
    re_path(r'^locker/$', views.locker, name='locker'),
    re_path(r'^locker/(?P<o_id>[0-9]+)/$', views.locker, name='locker'),
    re_path(r'^pwcont/$', views.pwcont, name='pwcont'),
    re_path(r'^pwcont/(?P<o_id>[0-9]+)/$', views.pwcont, name='pwcont'),
    re_path(r'^polyline/$', views.polyline, name='polyline'),
    re_path(r'^polyline/(?P<o_id>[0-9]+)/$', views.polyline, name='polyline'),

    re_path(r'^coup/(?P<o_id>[0-9]+)/links/$', views.coup_links, name='coup_links'),

    re_path(r'^coup/(?P<o_id>[0-9]+)/paint/$', views.coup_paint, name='coup_paint'),

    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', t_views.obtain_auth_token)

]
