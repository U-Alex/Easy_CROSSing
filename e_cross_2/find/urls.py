# find__urls

from django.urls import re_path

from . import views

urlpatterns = [

    re_path(r'^$', views.find_0, name='find_0'),
    re_path(r'^str=(?P<str_id>[0-9]+)/$', views.find_0, name='find_0'),
    re_path(r'^find_bu$', views.find_bu, name='find_bu'),
    re_path(r'^find_agr$', views.find_agr, name='find_agr'),
    re_path(r'^find_dev=(?P<param_id>[0-9]+)/$', views.find_dev, name='find_dev'),
    
    re_path(r'^map/$', views.maps, name='maps'),
    re_path(r'^map(?P<m_num>[1-5]+)/$', views.maps, name='maps'),
    re_path(r'^get_obj/$', views.get_obj, name='get_obj'),
    re_path(r'^js_request/$', views.js_request, name='js_request'),
    #url(r'^js_request_mess/$', views.js_request_mess, name='js_request_mess'),

]
