#

from django.urls import re_path

from . import views
from . import views_obj_mgr
from . import views_templ
from . import views_map_mgr
#from . import views_ext
#from . import views_mail

urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^logout/$', views.logout, name='logout'),

    re_path(r'^service/$', views.service, name='service'),
    re_path(r'^service/clean_his/$', views.service_clean_his, name='service_clean_his'),
    re_path(r'^switch_agr/$', views.switch_agr, name='switch_agr'),

    re_path(r'^o_manager/$', views_obj_mgr.o_manager, name='o_manager'),

    re_path(r'^m_manager(?P<m_num>[1-5]+)/$', views_map_mgr.m_manager, name='m_manager'),
    re_path(r'^m_manager(?P<m_num>[1-5]+)/cut/$', views_map_mgr.m_manager_cut, name='m_manager_cut'),
    re_path(r'^m_manager(?P<m_num>[1-5]+)/map_on/$', views_map_mgr.m_manager_map_on, name='m_manager_map_on'),
    re_path(r'^m_manager(?P<m_num>[1-5]+)/del=(?P<ftype>[1-2]+)/$', views_map_mgr.m_manager_del, name='m_manager_del'),

    re_path(r'^templ/$', views_templ.templ, name='templ'),
    re_path(r'^templ_lo=(?P<lo_id>[0-9]+)/$', views_templ.templ_lo, name='templ_lo'),
    re_path(r'^templ_lo_del=(?P<lo_id>[0-9]+)/$', views_templ.templ_lo_del, name='templ_lo_del'),
    re_path(r'^templ_cr=(?P<cr_id>[0-9]+)/$', views_templ.templ_cr, name='templ_cr'),
    re_path(r'^templ_cr_del=(?P<cr_id>[0-9]+)/$', views_templ.templ_cr_del, name='templ_cr_del'),
    re_path(r'^templ_dev=(?P<dev_id>[0-9]+)/$', views_templ.templ_dev, name='templ_dev'),
    re_path(r'^templ_dev_del=(?P<dev_id>[0-9]+)/$', views_templ.templ_dev_del, name='templ_dev_del'),
    re_path(r'^templ_box=(?P<box_id>[0-9]+)/$', views_templ.templ_box, name='templ_box'),
    re_path(r'^templ_box_del=(?P<box_id>[0-9]+)/$', views_templ.templ_box_del, name='templ_box_del'),
    re_path(r'^templ_box_cable=(?P<b_cab_id>[0-9]+)/$', views_templ.templ_box_cable, name='templ_box_cable'),
    re_path(r'^templ_box_cable_del=(?P<b_cab_id>[0-9]+)/$', views_templ.templ_box_cable_del, name='templ_box_cable_del'),
    re_path(r'^templ_su=(?P<su_id>[0-9]+)/$', views_templ.templ_su, name='templ_su'),
    re_path(r'^templ_su_del=(?P<su_id>[0-9]+)/$', views_templ.templ_su_del, name='templ_su_del'),
    re_path(r'^templ_cab=(?P<cab_id>[0-9]+)/$', views_templ.templ_cab, name='templ_cab'),
    re_path(r'^templ_cab_del=(?P<cab_id>[0-9]+)/$', views_templ.templ_cab_del, name='templ_cab_del'),
    re_path(r'^templ_coup=(?P<coup_id>[0-9]+)/$', views_templ.templ_coup, name='templ_coup'),
    re_path(r'^templ_coup_del=(?P<coup_id>[0-9]+)/$', views_templ.templ_coup_del, name='templ_coup_del'),

    # re_path(r'^new_kvar/$', views.new_kvar, name='new_kvar'),
    # re_path(r'^new_str/$', views.new_str, name='new_str'),
    # re_path(r'^new_bu/$', views.new_bu, name='new_bu'),

    re_path(r'^sprav/$', views.sprav, name='sprav'),
    re_path(r'^sprav_upr=(?P<upr_id>[0-9]+)/$', views.sprav_upr, name='sprav_upr'),
    re_path(r'^sprav_upr_del=(?P<upr_id>[0-9]+)/$', views.sprav_upr_del, name='sprav_upr_del'),

    re_path(r'^logs/u=(?P<u>[0-9]+)/td=(?P<td>[0-9]+)/$', views.show_all_logs, name='show_all_logs'),
    re_path(r'^logs/t=(?P<o_type>[0-9]+)/id=(?P<o_id>[0-9]+)/$', views.show_logs, name='show_logs'),

    #re_path(r'^block_ports=(?P<bu_id>[0-9]+)/$', views_ext.block_ports, name='block_ports'),
    #re_path(r'^dev_upd_config=(?P<dev_id>[0-9]+)/$', views_ext.dev_upd_config, name='dev_upd_config'),

    #re_path(r'^send_mail=(?P<bu_id>[0-9]+)/$', views_mail.send_mail_new_bu, name='send_mail_new_bu'),

    #url(r'^dev_send_rq_conf=(?P<dev_id>[0-9]+)/$', views.dev_send_rq_conf, name='dev_send_rq_conf'),
    #url(r'^incoming/$', views.dev_recieve_rq_conf, name='dev_recieve_rq_conf'),


]
