# cross__urls

from django.urls import re_path

from . import views
from . import views_objects
from . import views_links

urlpatterns = [

    re_path(r'^build=(?P<bu_id>[0-9]+)/$', views.show_bu_lo, name='show_bu_lo'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/$', views.show_bu_lo, name='show_bu_lo'),

    # re_path(r'^build=(?P<bu_id>[0-9]+)/$', views.show_build, name='show_build'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/edit/$', views_objects.edit_build, name='edit_build'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/new_locker/$', views_objects.new_locker, name='new_locker'),
    # re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/$', views.show_locker, name='show_locker'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/edit/$', views_objects.edit_locker, name='edit_locker'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/energy/$', views.energy, name='energy'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/new_cr/$', views_objects.new_cr, name='new_cr'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/new_dev/$', views_objects.new_dev, name='new_dev'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/new_box/$', views_objects.new_box, name='new_box'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/new_su/$', views_objects.new_su, name='new_su'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/$', views.show_cr, name='show_cr'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/$', views.show_dev, name='show_dev'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/l2=(?P<l2>[0-1]+)/$', views.show_dev, name='show_dev'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/$', views.show_box, name='show_box'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/del_locker=(?P<lo_id>[0-9]+)/$', views_objects.del_locker, name='del_locker'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/del_cross=(?P<cr_id>[0-9]+)/$', views_objects.del_cross, name='del_cross'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/del_dev=(?P<dev_id>[0-9]+)/$', views_objects.del_dev, name='del_dev'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/del_box=(?P<box_id>[0-9]+)/$', views_objects.del_box, name='del_box'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/del_subunit=(?P<su_id>[0-9]+)/$', views_objects.del_subunit, name='del_subunit'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/edit/$', views_objects.edit_cr, name='edit_cr'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/p_edit=(?P<p_id>[0-9]+)/$', views_objects.edit_cr_p, name='edit_cr_p'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/edit/$', views_objects.edit_dev, name='edit_dev'),
    #re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/info/$', views_objects.info_dev, name='info_dev'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/p_edit=(?P<p_id>[0-9]+)/$', views_objects.edit_dev_p, name='edit_dev_p'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/add_v_port/$', views_objects.add_v_port, name='add_v_port'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/edit_f_port=(?P<f_p_id>[0-9]+)/$', views_objects.edit_dev_p_v, name='edit_dev_p_v'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/edit_v_port=(?P<v_p_id>[0-9]+)/$', views_objects.edit_dev_p_v, name='edit_dev_p_v'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/del_v_port=(?P<v_p_id>[0-9]+)/$', views_objects.del_v_port, name='del_v_port'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/edit/$', views_objects.edit_box, name='edit_box'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/p_edit=(?P<p_id>[0-9]+)/$', views_objects.edit_box_p, name='edit_box_p'),
    
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/subunit=(?P<su_id>[0-9]+)/$', views_objects.edit_subunit, name='edit_subunit'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/ext_cr1/$', views_links.ext_cr1, name='ext_cr1'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/ext_cr2=(?P<d_bu_id>[0-9]+)/$', views_links.ext_cr2, name='ext_cr2'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/ext_cr2=(?P<d_bu_id>[0-9]+)/d_p=(?P<d_port_id>[0-9]+)/$', views_links.ext_ok, name='ext_ok'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<cr_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/del_cr/$', views_links.del_cr, name='del_ext_cr'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<s_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/$', views_links.int_c, name='int_c'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<s_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/$', views_links.int_c, name='int_c'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<s_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/$', views_links.int_c, name='int_c'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<s_id>[0-9]+)/del=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/$', views_links.del_int_c, name='del_int_c'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<s_id>[0-9]+)/del=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/$', views_links.del_int_c, name='del_int_c'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<s_id>[0-9]+)/del=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/$', views_links.del_int_c, name='del_int_c'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/cr=(?P<s_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/d_p=(?P<d_port_id>[0-9]+)/d_type=(?P<d_type>[0-9]+)/$', views_links.int_ok, name='int_ok'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<s_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/d_p=(?P<d_port_id>[0-9]+)/d_type=(?P<d_type>[0-9]+)/$', views_links.int_ok, name='int_ok'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<s_id>[0-9]+)/s_p=(?P<s_port_id>[0-9]+)/s_type=(?P<s_type>[0-9]+)/d_p=(?P<d_port_id>[0-9]+)/d_type=(?P<d_type>[0-9]+)/$', views_links.int_ok, name='int_ok'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/s_p=(?P<port_id>[0-9]+)/cr_ab/$', views_links.cr_ab, name='cr_ab'),
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/s_p=(?P<port_id>[0-9]+)/del_ab=(?P<pri>[0-9]+)/$', views_links.del_ab, name='del_ab'),

    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/s_p=(?P<port_id>[0-9]+)/cr_su=(?P<su_id>[0-9]+)/$', views_links.cr_su, name='cr_su'),
    #re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/box=(?P<box_id>[0-9]+)/s_p=(?P<port_id>[0-9]+)/del_su=(?P<pri>[0-9]+)/$', views_links.del_su, name='del_su'),
    
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/racks/$', views.show_racks, name='show_racks'),
    
    re_path(r'^build=(?P<bu_id>[0-9]+)/locker=(?P<lo_id>[0-9]+)/dev=(?P<dev_id>[0-9]+)/ips/$', views.show_dev_ips, name='show_dev_ips'),
    
]
