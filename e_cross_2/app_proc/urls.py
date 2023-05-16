#

from django.urls import re_path

from . import views
#from . import views_ext

urlpatterns = [
    #re_path(r'^$', views.index, name='index'),
    #re_path(r'^$', views.app, name='app'),
    re_path(r'^status=(?P<status>[0-9]+)/$', views.app, name='app'),
    re_path(r'^status=(?P<status>[0-9]+)/sort/$', views.app_sort, name='app_sort'),
    re_path(r'^status=(?P<status>[0-9]+)/app_find/$', views.app_find, name='app_find'),
    re_path(r'^add_app/$', views.add_app, name='add_app'),
    #re_path(r'^new_app/$', views.new_app, name='new_app'),
    re_path(r'^edit=(?P<app_id>[0-9]+)/$', views.edit, name='edit'),

    re_path(r'^install=(?P<app_id>[0-9]+)/$', views.app_install, name='app_install'),
    re_path(r'^install=(?P<app_id>[0-9]+)/sel=(?P<box_p_id>[0-9]+)/$', views.app_install, name='app_install'),
    re_path(r'^install=(?P<app_id>[0-9]+)/reject/$', views.app_reject, name='app_reject'),
    re_path(r'^install=(?P<app_id>[0-9]+)/delay/$', views.app_delay, name='app_delay'),
    re_path(r'^install=(?P<app_id>[0-9]+)/to_inbox/$', views.to_inbox, name='to_inbox'),
    re_path(r'^install=(?P<app_id>[0-9]+)/complete/$', views.app_complete, name='app_complete'),
    re_path(r'^install=(?P<app_id>[0-9]+)/check=(?P<check>[0-9]+)/$', views.app_check, name='app_check'),

    re_path(r'^remove=(?P<app_id>[0-9]+)/$', views.app_remove, name='app_remove'),
    re_path(r'^remove=(?P<app_id>[0-9]+)/reject/$', views.app_reject2, name='app_reject2'),
    re_path(r'^remove=(?P<app_id>[0-9]+)/complete/$', views.app_complete2, name='app_complete2'),
    #re_path(r'^remove=(?P<app_id>[0-9]+)/send/$', views_ext.nsd_unset_send_hand, name='nsd_unset_send_hand'),

    re_path(r'^gen_pdf_0=(?P<app_id>[0-9]+)/$', views.gen_pdf_0, name='gen_pdf_0'),
    re_path(r'^gen_pdf_1=(?P<app_id>[0-9]+)/$', views.gen_pdf_1, name='gen_pdf_1'),
    re_path(r'^gen_pdf_2=(?P<box_p_id>[0-9]+)/$', views.gen_pdf_2, name='gen_pdf_2'),
    #re_path(r'^from_bgb/$', views.from_bgb, name='from_bgb'),
    
    re_path(r'^show_logs_nsd/td=(?P<td>[0-9]+)/$', views.show_logs_nsd, name='show_logs_nsd'),
    #re_path(r'^nsd/unset/$', views_ext.nsd_unset, name='nsd_unset'),
    #re_path(r'^nsd/unset_ok/$', views_ext.nsd_unset_ok, name='nsd_unset_ok'),

]
