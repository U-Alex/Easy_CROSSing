# core__views_templ

#import datetime
#import time
#import requests

#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
#from django.views.decorators.csrf import csrf_exempt

#from cross.models import Kvartal, Street, Building
from cross.models import Locker, Cross, Device, Box, Subunit
from cross.models import Device_ports, Box_ports
from core.models import Templ_locker, Templ_cross, Templ_device, Templ_box_cable, Templ_box, Templ_subunit
from cable.models import Templ_cable, Coupling, Coupling_ports, Templ_coupling

#from .forms import n_kvar_Form, n_str_Form, n_bu_Form, sprav_upr_Form
from .forms import templ_lo_Form, templ_cr_Form, templ_dev_Form, templ_box_Form, templ_su_Form
from .forms import templ_box_cable_Form, templ_cab_Form, templ_coup_Form

#from core.shared_def import to_his
from core.e_config import conf

####################################################################################################

@login_required(login_url='/core/login/')
def templ(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    
    return render(request, 'templ.html', {'lo_list': Templ_locker.objects.all().order_by('id'),
                                          'cr_list': Templ_cross.objects.all().order_by('id'),
                                          'dev_list': Templ_device.objects.all().order_by('parrent_id', 'id'),
                                          'box_list': Templ_box.objects.all().order_by('id'),
                                          'box_cable_list': Templ_box_cable.objects.all().order_by('id'),
                                          'su_list': Templ_subunit.objects.all().order_by('parrent_id', 'name'),
                                          'cable_list': Templ_cable.objects.all().order_by('capacity', 'name'),
                                          'coup_list': Templ_coupling.objects.all().order_by('id'),
                                          })


###############################--locker--###########################################################

@login_required(login_url='/core/login/')
def templ_lo(request, lo_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        lo = Templ_locker.objects.get(pk=lo_id) if (lo_id != '0') else 0
    except ObjectDoesNotExist:
        lo = 0
        lo_id = '0'
    if request.method == 'POST':
        if lo_id != '0':
            form = templ_lo_Form(request.POST, instance=lo)
            ch_lo = Locker.objects.filter(con_type=lo.id).update(name_type=form.data['name'].strip())
        else:
            form = templ_lo_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_lo_Form(instance=lo) if (lo_id != '0') else templ_lo_Form()

    return render(request, 'templ_lo.html', {'form': form, 'lo': lo})


@login_required(login_url='/core/login/')
def templ_lo_del(request, lo_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        lo = Templ_locker.objects.get(pk=lo_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Locker.objects.filter(con_type=int(lo.id)).exists() else True
    if request.method == 'POST' and del_ok:
        lo.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'lo': lo,
                                              'del_ok': del_ok,
                                              'count': Locker.objects.filter(con_type=int(lo.id)).count(),
                                              })

###############################--cross--############################################################

@login_required(login_url='/core/login/')
def templ_cr(request, cr_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'не достаточно прав', 'back': 2})
    try:
        cr = Templ_cross.objects.get(pk=cr_id) if (cr_id != '0') else 0
    except ObjectDoesNotExist:
        cr = 0
        cr_id = '0'
    if request.method == 'POST':
        if cr_id != '0':
            form = templ_cr_Form(request.POST, instance=cr)
            try:
                v_forw_l_r = True if (form.data['v_forw_l_r']) else False
            except:
                v_forw_l_r = False
            ch_cr = Cross.objects.filter(con_type=cr.id).update(name_type=form.data['name'].strip(),
                                                                v_col=form.data['v_col'],
                                                                v_row=form.data['v_row'],
                                                                v_forw_l_r=v_forw_l_r
                                                                )
        else:
            form = templ_cr_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_cr_Form(instance=cr) if (cr_id != '0') else templ_cr_Form()

    return render(request, 'templ_cr.html', {'form': form, 'cr': cr})


@login_required(login_url='/core/login/')
def templ_cr_del(request, cr_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        cr = Templ_cross.objects.get(pk=cr_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Cross.objects.filter(con_type=int(cr.id)).exists() else True
    if request.method == 'POST' and del_ok:
        cr.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'cr': cr,
                                              'del_ok': del_ok,
                                              'count': Cross.objects.filter(con_type=int(cr.id)).count(),
                                              })

###############################--device--###########################################################

@login_required(login_url='/core/login/')
def templ_dev(request, dev_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        dev = Templ_device.objects.get(pk=dev_id) if (dev_id != '0') else 0
    except ObjectDoesNotExist:
        dev = 0
        dev_id = '0'
    if request.method == 'POST':
        if dev_id != '0':
            form = templ_dev_Form(request.POST, instance=dev)
            ch_dev = Device.objects.filter(con_type=dev.id)
            ch_dev.update(name_type=form.data['name'].strip())
            if (dev.port_alias_list != form.data['port_alias_list']) or (dev.port_t_x_list != form.data['port_t_x_list']) or (dev.port_speed_list != form.data['port_speed_list']):
                ch_dev_ports = Device_ports.objects.filter(parrent_id__con_type=dev.id)
                alias_list = form.data['port_alias_list'].split(',')
                t_x_list = form.data['port_t_x_list'].split(',')
                speed_list = form.data['port_speed_list'].split(',')
                i = 0
                while i < len(alias_list):
                    i += 1
                    ch_dev_ports.filter(num=i).update(p_alias=alias_list[i-1].strip(),
                                                      port_t_x=t_x_list[i-1].strip(),
                                                      port_speed=speed_list[i-1].strip()
                                                      )
        else:
            form = templ_dev_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_dev_Form(instance=dev) if (dev_id != '0') else templ_dev_Form()

    return render(request, 'templ_dev.html', {'form': form, 'dev': dev})


@login_required(login_url='/core/login/')
def templ_dev_del(request, dev_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        dev = Templ_device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Device.objects.filter(con_type=int(dev.id)).exists() else True
    if request.method == 'POST' and del_ok:
        dev.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'dev': dev,
                                              'del_ok': del_ok,
                                              'count': Device.objects.filter(con_type=int(dev.id)).count(),
                                              })

###############################--box--##############################################################

@login_required(login_url='/core/login/')
def templ_box(request, box_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        box = Templ_box.objects.get(pk=box_id) if (box_id != '0') else 0
    except ObjectDoesNotExist:
        box = 0
        box_id = '0'
    if request.method == 'POST':
        if box_id != '0':
            form = templ_box_Form(request.POST, instance=box)
            if box.name != form.data['name'].strip():
                ch_box = Box.objects.filter(con_type=box.id)
                ch_box.update(name_type=form.data['name'].strip())
        else:
            form = templ_box_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_box_Form(instance=box) if (box_id != '0') else templ_box_Form()

    return render(request, 'templ_box.html', {'form': form, 'box': box})


@login_required(login_url='/core/login/')
def templ_box_del(request, box_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        box = Templ_box.objects.get(pk=box_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Box.objects.filter(con_type=int(box.id)).exists() else True
    if request.method == 'POST' and del_ok:
        box.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'box': box,
                                              'del_ok': del_ok,
                                              'count': Box.objects.filter(con_type=int(box.id)).count(),
                                              })

###############################--box_cable--#######################################################

@login_required(login_url='/core/login/')
def templ_box_cable(request, b_cab_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        box_cab = Templ_box_cable.objects.get(pk=b_cab_id) if (b_cab_id != '0') else 0
    except ObjectDoesNotExist:
        box_cab = 0
        b_cab_id = '0'
    if request.method == 'POST':
        if b_cab_id != '0':
            form = templ_box_cable_Form(request.POST, instance=box_cab)
            if box_cab.alias_list != form.data['alias_list']:
                ch_box_ports = Box_ports.objects.filter(cable_id=box_cab.id)
                alias_list = form.data['alias_list'].split(',')
                i = 0
                while i < len(alias_list):
                    i += 1
                    ch_box_ports.filter(num=i).update(p_alias=alias_list[i-1].strip())
        else:
            form = templ_box_cable_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_box_cable_Form(instance=box_cab) if (b_cab_id != '0') else templ_box_cable_Form()

    return render(request, 'templ_box_cable.html', {'form': form, 'box_cab': box_cab})


@login_required(login_url='/core/login/')
def templ_box_cable_del(request, b_cab_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        box_cab = Templ_box_cable.objects.get(pk=b_cab_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Box_ports.objects.filter(cable_id=int(box_cab.id)).exists() else True
    if request.method == 'POST' and del_ok:
        box_cab.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'box_cab': box_cab,
                                              'del_ok': del_ok,
                                              'count': Box_ports.objects.filter(cable_id=int(box_cab.id)).count(),
                                              })

###############################--subunit--##########################################################

@login_required(login_url='/core/login/')
def templ_su(request, su_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        su = Templ_subunit.objects.get(pk=su_id) if (su_id != '0') else 0
    except ObjectDoesNotExist:
        su = 0
        su_id = '0'
    if request.method == 'POST':
        if su_id != '0':
            form = templ_su_Form(request.POST, instance=su)
            #ch_su = Locker.objects.filter(con_type=lo.id).update(name_type=form.data['name'].strip())
        else:
            form = templ_su_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_su_Form(instance=su) if (su_id != '0') else templ_su_Form()

    return render(request, 'templ_su.html', {'form': form, 'su': su})


@login_required(login_url='/core/login/')
def templ_su_del(request, su_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        su = Templ_subunit.objects.get(pk=su_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Subunit.objects.filter(con_type=int(su.id)).exists() else True
    if request.method == 'POST' and del_ok:
        su.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'su': su,
                                              'del_ok': del_ok,
                                              'count': Subunit.objects.filter(con_type=int(su.id)).count(),
                                              })

###############################--cable--############################################################

@login_required(login_url='/core/login/')
def templ_cab(request, cab_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        cab = Templ_cable.objects.get(pk=cab_id) if (cab_id != '0') else 0
    except ObjectDoesNotExist:
        cab = 0
        cab_id = '0'
    if request.method == 'POST':
        if cab_id != '0':
            form = templ_cab_Form(request.POST, instance=cab)
            if (cab.mod_capa_list != form.data['mod_capa_list']) or (cab.mod_color_list != form.data['mod_color_list']) or (cab.fiber_colors_list != form.data['fiber_colors_list']):
                ch_cab_ports = Coupling_ports.objects.filter(cable_type=cab.id)
                mod_capa_list = form.data['mod_capa_list'].split(',')
                mod_color_list = form.data['mod_color_list'].split(',')
                fiber_colors_list = form.data['fiber_colors_list'].split(',')
                i = 0
                while i < len(fiber_colors_list):
                    i += 1
                    mod_num = int(mod_capa_list[i-1].split('-')[1].strip())
                    ch_cab_ports.filter(fiber_num=i).update(mod_num=mod_num,
                                                            mod_color=mod_color_list[mod_num-1].strip(),
                                                            fiber_color=fiber_colors_list[i-1].strip()
                                                            )
        else:
            form = templ_cab_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_cab_Form(instance=cab) if (cab_id != '0') else templ_cab_Form()

    return render(request, 'templ_cab.html', {'form': form, 'cab': cab, 'colors': conf.RU_COLOR_LIST.items()})


@login_required(login_url='/core/login/')
def templ_cab_del(request, cab_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        cab = Templ_cable.objects.get(pk=cab_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Coupling_ports.objects.filter(cable_type=int(cab.id)).exists() else True
    count = Coupling_ports.objects.filter(fiber_num=1, cable_type=int(cab.id)).count() / 2
    if request.method == 'POST' and del_ok:
        cab.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'cab': cab,
                                              'del_ok': del_ok,
                                              'count': int(count),
                                              })

###############################--coupling--#########################################################

@login_required(login_url='/core/login/')
def templ_coup(request, coup_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        coup = Templ_coupling.objects.get(pk=coup_id) if (coup_id != '0') else 0
    except ObjectDoesNotExist:
        coup = 0
        coup_id = '0'
    if request.method == 'POST':
        if coup_id != '0':
            form = templ_coup_Form(request.POST, instance=coup)
            ch_coup = Coupling.objects.filter(name_type=coup.name).update(name_type=form.data['name'].strip())
        else:
            form = templ_coup_Form(request.POST)
        form.save()

        return HttpResponseRedirect('/core/templ/')
    else:
        form = templ_coup_Form(instance=coup) if (coup_id != '0') else templ_coup_Form()

    return render(request, 'templ_coup.html', {'form': form, 'coup': coup})


@login_required(login_url='/core/login/')
def templ_coup_del(request, coup_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})
    try:
        coup = Templ_coupling.objects.get(pk=coup_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    del_ok = False if Coupling.objects.filter(name_type=coup.name).exists() else True
    if request.method == 'POST' and del_ok:
        coup.delete()
        return HttpResponseRedirect('/core/templ/')

    return render(request, 'templ_del.html', {'coup': coup,
                                              'del_ok': del_ok,
                                              'count': Coupling.objects.filter(name_type=coup.name).count(),
                                              })

####################################################################################################
