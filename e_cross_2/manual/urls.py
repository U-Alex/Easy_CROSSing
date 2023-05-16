#

from django.urls import re_path

from . import views

urlpatterns = [

    re_path(r'^$', views.man, name='man'),
    re_path(r'^(?P<l1>[0-9]+)/$', views.man, name='man'),

]
