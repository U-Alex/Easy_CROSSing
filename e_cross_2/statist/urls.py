#

from django.urls import re_path

from . import views

urlpatterns = [
    
    re_path(r'^stat_subunit/$', views.stat_subunit, name='stat_subunit'),
    re_path(r'^stat_subunit/f=(?P<s_f>[0-1]+)/c=(?P<s_col>[0-9]+)/t=(?P<t_curr>[0-9]+)/$', views.stat_subunit, name='stat_subunit'),
    re_path(r'^stat_subunit/f=(?P<s_f>[0-1]+)/c=(?P<s_col>[0-9]+)/t=(?P<t_curr>[0-9]+)/xls=(?P<xls>[0-1]+)/$', views.stat_subunit, name='stat_subunit'),

    re_path(r'^null_len/$', views.cable_null_len, name='cable_null_len'),
    re_path(r'^coup_changed/$', views.coup_changed, name='coup_changed'),

    re_path(r'^bu_doc=(?P<bu_id>[0-9]+)/$', views.bu_doc, name='bu_doc'),
    re_path(r'^bu_doc_del=(?P<bu_id>[0-9]+)/$', views.bu_doc_del, name='bu_doc_del'),

    re_path(r'^sync_co_lo/$', views.sync_Coup_lo, name='sync_Coup_lo'),
    re_path(r'^check_link/$', views.check_link, name='check_link'),
    re_path(r'^obj_no_coord/$', views.obj_no_coord, name='obj_no_coord'),
    re_path(r'^dev_no_sn_mac/$', views.dev_no_sn_mac, name='dev_no_sn_mac'),
    re_path(r'^duple_dog/$', views.duple_dog, name='duple_dog'),

    re_path(r'^agr_to_abon=(?P<dev_id>[0-9]+)/$', views.agr_to_abon, name='agr_to_abon'),
    
]
