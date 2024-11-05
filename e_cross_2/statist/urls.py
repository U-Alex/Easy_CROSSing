#

from django.urls import re_path

from . import views

urlpatterns = [

    re_path(r'^$', views.stat, name='stat'),
    re_path(r'^stat2/$', views.stat2, name='stat2'),
    re_path(r'^stat3/$', views.stat3, name='stat3'),
    re_path(r'^stat4/$', views.stat4, name='stat4'),
    re_path(r'^stat_energy/$', views.stat_energy, name='stat_energy'),

    re_path(r'^building/$', views.stat_bu, name='stat_bu'),
    re_path(r'^lockers/$', views.stat_lo, name='stat_lo'),
    re_path(r'^lockers_det/$', views.stat_lo_det, name='stat_lo_det'),
    re_path(r'^lockers_noco/$', views.stat_lo_noco, name='stat_lo_noco'),

    re_path(r'^dev_type/(?P<t_id>[0-9]+)/$', views.stat_dev_type, name='stat_dev_type'),
    re_path(r'^dev_all/$', views.stat_dev_all, name='stat_dev_all'),
    re_path(r'^dev_br/$', views.stat_dev_br, name='stat_dev_br'),
    re_path(r'^dev_bad/$', views.stat_dev_bad, name='stat_dev_bad'),

    re_path(r'^box_br=(?P<co>[0-9]+)/$', views.stat_box_br, name='stat_box_br'),
    re_path(r'^box_bad/$', views.stat_box_bad, name='stat_box_bad'),
    re_path(r'^box_uninstall/$', views.stat_box_uninstall, name='stat_box_uninstall'),      ### del
    
    re_path(r'^stat_subunit/$', views.stat_subunit, name='stat_subunit'),
    re_path(r'^stat_subunit/f=(?P<s_f>[0-1]+)/c=(?P<s_col>[0-9]+)/t=(?P<t_curr>[0-9]+)/$', views.stat_subunit, name='stat_subunit'),
    re_path(r'^stat_subunit/f=(?P<s_f>[0-1]+)/c=(?P<s_col>[0-9]+)/t=(?P<t_curr>[0-9]+)/xls=(?P<xls>[0-1]+)/$', views.stat_subunit, name='stat_subunit'),

    re_path(r'^stat_block_ports/$', views.stat_block_ports, name='stat_block_ports'),

    re_path(r'^null_len/$', views.cable_null_len, name='cable_null_len'),
    re_path(r'^coup_changed/$', views.coup_changed, name='coup_changed'),

    re_path(r'^bu_doc=(?P<bu_id>[0-9]+)/$', views.bu_doc, name='bu_doc'),
    re_path(r'^bu_doc_del=(?P<bu_id>[0-9]+)/$', views.bu_doc_del, name='bu_doc_del'),

    #re_path(r'^bil/id=(?P<p_id>[0-9]+)/$', views.res_for_bil, name='res_for_bil'),

    re_path(r'^sync_co_lo/$', views.sync_Coup_lo, name='sync_Coup_lo'),
    re_path(r'^check_link/$', views.check_link, name='check_link'),
    re_path(r'^obj_no_coord/$', views.obj_no_coord, name='obj_no_coord'),
    # re_path(r'^dev_no_sn_mac/$', views.dev_no_sn_mac, name='dev_no_sn_mac'),
    re_path(r'^duple_dog/$', views.duple_dog, name='duple_dog'),
    # re_path(r'^check_dog/$', views.check_dog, name='check_dog'),            ### del

    re_path(r'^get_ip_list=(?P<con_type>[0-9]+)/$', views.get_ip_list, name='get_ip_list'),

    re_path(r'^agr_to_abon=(?P<dev_id>[0-9]+)/$', views.agr_to_abon, name='agr_to_abon'),
    re_path(r'^suspicious_ip/$', views.suspicious_ip, name='suspicious_ip'),
    re_path(r'^stat_last_update_config/$', views.stat_last_update_config, name='stat_last_update_config'),
    re_path(r'^stat_log_update_config/$', views.stat_log_update_config, name='stat_log_update_config'),
    #url(r'^talkback/$', views.talkback, name='talkback'),

]
