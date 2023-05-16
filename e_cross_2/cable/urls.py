# cable__urls

from django.urls import re_path

from . import views

urlpatterns = [

    re_path(r'^$', views.cable_main, name='cable_main'),

    re_path(r'^kv=(?P<kvar>[0-9]+)/pw_add/$', views.pw_add, name='pw_add'),
    re_path(r'^kv=(?P<kvar>[0-9]+)/pw_edit=(?P<s_pw>[0-9]+)/$', views.pw_edit, name='pw_edit'),
    re_path(r'^kv=(?P<kvar>[0-9]+)/pw_del=(?P<s_pw>[0-9]+)/$', views.pw_del, name='pw_del'),

    re_path(r'^kv=(?P<kvar>[0-9]+)/coup_add/p_t=(?P<p_t>[0-9]+)/p_id=(?P<p_id>[0-9]+)/$', views.coup_add, name='coup_add'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/$', views.coup_view, name='coup_view'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/coup_edit/$', views.coup_edit, name='coup_edit'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/coup_del/$', views.coup_del, name='coup_del'),

    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_up=(?P<cab_num>[0-9]+)/$', views.cab_up, name='cab_up'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_add=(?P<kvar>[0-9]+)/$', views.cab_add1, name='cab_add1'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_add=(?P<kvar>[0-9]+)/target=(?P<d_coup>[0-9]+)/$', views.cab_add2, name='cab_add2'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_move=(?P<kvar>[0-9]+)/cab=(?P<cab>[0-9]+)/$', views.cab_move1, name='cab_move1'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_move=(?P<kvar>[0-9]+)/cab=(?P<cab>[0-9]+)/target=(?P<d_coup>[0-9]+)/$', views.cab_move2, name='cab_move2'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_edit=(?P<p_id>[0-9]+)/$', views.cab_edit, name='cab_edit'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/cab_del=(?P<cab>[0-9]+)/$', views.cab_del, name='cab_del'),

    re_path(r'^coup=(?P<s_coup>[0-9]+)/int_c=(?P<s_port>[0-9]+)/stat=(?P<stat>[0-9]+)/m=(?P<multi>[0-1]+)/$', views.int_c, name='int_c'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/int_c=(?P<s_port>[0-9]+)/stat=(?P<stat>[0-9]+)/m=(?P<multi>[0-1]+)/dest=(?P<dest_type>[0-9]+)/$', views.int_c, name='int_c'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/int_edit=(?P<p_id>[0-9]+)/$', views.int_edit, name='int_edit'),
    re_path(r'^coup=(?P<s_coup>[0-9]+)/int_del=(?P<s_port>[0-9]+)/$', views.int_del, name='int_del'),

    re_path(r'^chain=(?P<p_id>[0-9]+)/p_type=(?P<p_type>[0-1]+)/$', views.chain, name='chain'),

]
