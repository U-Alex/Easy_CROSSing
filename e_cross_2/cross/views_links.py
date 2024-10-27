# cross__views_links

import datetime
import re

from django.shortcuts import render
#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
#from django.core.exceptions import ObjectDoesNotExist

from .models import Kvartal, Building
from .models import Locker, Cross, Device, Box, Subunit
from .models import Cross_ports, Device_ports, Box_ports
from core.models import Templ_subunit

#from .forms import find_Form_bu
from find.forms import find_Form_bu
from .forms import sel_up_status_Form
from .forms import cr_ab_Form, del_ab_Form

from core.shared_def import to_his
from core.e_config import conf

####################################################################################################


@login_required(login_url='/core/login/')
def ext_cr1(request, bu_id, lo_id, cr_id, s_port_id):

    if not request.user.has_perm("core.can_ext"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    agr = Locker.objects.filter(agr=True).order_by('co')
    lo = Locker.objects.filter(agr=False, status__in=(0, 1)).order_by('co')
    s_p_id = Cross_ports.objects.get(pk=s_port_id)
    s_p_title = (s_p_id.parrent.parrent.parrent.name,
                 s_p_id.parrent.parrent.parrent.house_num,
                 s_p_id.parrent.parrent.name,
                 s_p_id.parrent.name,
                 s_p_id.num)
    if request.method == 'POST':
        form = find_Form_bu(request.POST)
        if form.is_valid():
            street_id = form.cleaned_data['street']
            #street_name = Street.objects.get(pk=street_id).name
            h_num = form.cleaned_data['house_num']
            bu = Building.objects.filter(parrent_id=street_id).order_by('house_num')
            context = {#'s_p_id': s_p_id,
                       'str_list': bu,
                       'str_id': street_id,
                       'f_edit': True,
                       's_p_title': s_p_title
                       }
            if (bu.count()) == 0:
                return HttpResponseRedirect('../ext_cr1')
            if h_num != '':
                bu2 = bu.filter(house_num=h_num)
                if (bu2.count()) != 1:
                    return render(request, 'ext_cr1.html', context)
                build = bu2.values('id')[0]['id']
                return HttpResponseRedirect(f"../ext_cr2={build}")

            return render(request, 'ext_cr1.html', context)
    else:
        form = find_Form_bu(initial={'street': 0})

    return render(request, 'ext_cr1.html', {#'s_p_id': s_p_id,
                                            'form': form,
                                            'agr': agr,
                                            'lo': lo,
                                            's_p_title': s_p_title
                                            })


@login_required(login_url='/core/login/')
def ext_cr2(request, bu_id, lo_id, cr_id, s_port_id, d_bu_id):

    if not request.user.has_perm("core.can_ext"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    lo_list = Locker.objects.filter(parrent_id=d_bu_id).order_by('-agr', 'id').values()
    if not lo_list.exists():
        return HttpResponseRedirect('../ext_cr1/')  #УД нет
    bu2 = Building.objects.get(pk=d_bu_id)
    cr_val = False                                  #по-умолчанию кросса нет
    for lo_ob in lo_list:
        cr = Cross.objects.filter(parrent_id=lo_ob['id']).order_by('name').values()
        if cr.exists():
            cr_val = True
        for cr_ob in cr:
            cr_ob_p = Cross_ports.objects.filter(parrent_id=cr_ob['id'])#.order_by('num')
            cr_p_h = []                         #кол-во портов по ширине

            v_row = cr_ob['v_col']
            v_col = cr_ob['v_row']
            if cr_ob['v_forw_l_r']:
                v_row, v_col = v_col, v_row
            p_count = 0
            for _ in range(v_row):
                cr_p_v = []                     #кол-во портов по высоте
                for _ in range(v_col):
                    p_count += 1
                    curr_p = cr_ob_p.get(num=p_count)
                    cr_p_v.append((curr_p.id,                           #0
                                   curr_p.num,                          #1
                                   curr_p.up_status,                    #2
                                   curr_p.p_valid,                      #3
                                   curr_p.prim                          #4
                                   #conf.COLOR_CROSS[curr_p.up_status],  #5  ######
                                   ))
                cr_p_h.append(cr_p_v)

            if not cr_ob['v_forw_l_r']:
                #cr_p_h = cr_tr_matrix(v_col, v_row, cr_p_h)
                cr_p_h = zip(*cr_p_h)
            cr_ob['cr_p'] = cr_p_h

        lo_ob['cr'] = cr

    if not cr_val:
        return HttpResponseRedirect('../ext_cr1/')

    s_p_id = Cross_ports.objects.get(pk=s_port_id)
    s_p_title = (s_p_id.parrent.parrent.parrent.name,
                 s_p_id.parrent.parrent.parrent.house_num,
                 s_p_id.parrent.parrent.name,
                 s_p_id.parrent.name,
                 s_p_id.num)

    return render(request, 'ext_cr2.html', {#'s_p_id': s_p_id,
                                            'bu2': bu2,
                                            'lo': lo_list,
                                            's_p_title': s_p_title
                                            })


# def cr_tr_matrix(v_col, v_row, cr_p_h):
#
#     cr_p_h2 = []
#     row = 0
#     while row < v_col:
#         row += 1
#         cr_p_v2 = []
#         col = 0
#         while col < v_row:
#             col += 1
#             cr_p_v2.append(cr_p_h[col-1][row-1])
#         cr_p_h2.append(cr_p_v2)
#
#     return cr_p_h2


@login_required(login_url='/core/login/')
def ext_ok(request, bu_id, lo_id, cr_id, s_port_id, d_bu_id, d_port_id):

    if not request.user.has_perm("core.can_ext"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    s_p_id = Cross_ports.objects.get(pk=s_port_id)
    d_p_id = Cross_ports.objects.get(pk=d_port_id)
    if s_port_id == d_port_id:
        return HttpResponseRedirect('../')

    if request.method == 'POST':
        form = sel_up_status_Form(request.POST)
        if form.is_valid():
            sel_status = form.cleaned_data['status']
            with transaction.atomic():
                if s_p_id.up_status != 0:
                    return render(request, 'error.html', {'mess': 's_p_id.up_status != 0', 'back': 3})
                if d_p_id.up_status != 0:
                    return render(request, 'error.html', {'mess': 'd_p_id.up_status != 0', 'back': 3})
                s_p_id.up_cross_id = d_port_id
                s_p_id.up_status = sel_status
                d_p_id.up_cross_id = s_port_id
                d_p_id.up_status = sel_status
                s_p_id.save()
                d_p_id.save()

                h_text = 'УД: '+s_p_id.parrent.parrent.name+' кросс: '+s_p_id.parrent.name+' порт: '+str(s_p_id.num)
                h_text += ' >>> УД: '+d_p_id.parrent.parrent.name+' кросс: '+d_p_id.parrent.name+' порт: '+str(d_p_id.num)
                h_text += ' >>>  status: '+conf.STATUS_LIST[int(s_p_id.up_status)][1]
                to_his([request.user, 5, s_p_id.id, 3, 0, h_text])
                to_his([request.user, 5, d_p_id.id, 3, 0, h_text])

            return HttpResponseRedirect(f"../../../?sel={s_port_id}")
    else:
        form = sel_up_status_Form(initial={'status': 1})

    return render(request, 'ext_sel_status.html', {'s_p_id': s_p_id, 'd_p_id': d_p_id, 'form': form,})


@login_required(login_url='/core/login/')
def del_cr(request, bu_id, lo_id, cr_id, s_port_id):

    if not request.user.has_perm("core.can_ext"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    s_p = Cross_ports.objects.get(pk=s_port_id)
    d_p = Cross_ports.objects.get(pk=s_p.up_cross_id)
    if request.method == 'POST':
        with transaction.atomic():
            if s_p.up_status == 0:
                return render(request, 'error.html', {'mess': 's_p.up_status == 0', 'back': 2})
            if d_p.up_status == 0:
                return render(request, 'error.html', {'mess': 'd_p.up_status == 0', 'back': 2})
            s_p.up_cross_id = 0
            s_p.up_status = 0
            d_p.up_cross_id = 0
            d_p.up_status = 0
            t_opt = f"{s_p.opt_len}/{d_p.opt_len}"
            s_p.opt_len = 0
            d_p.opt_len = 0
            s_p.save()
            d_p.save()

            h_text = f'УД: {s_p.parrent.parrent.name} кросс: {s_p.parrent.name} порт: {s_p.num} >>> '
            h_text += f'УД: {d_p.parrent.parrent.name} кросс: {d_p.parrent.name} порт: {d_p.num} >>>  опт.дл.: {t_opt}'
            to_his([request.user, 5, s_p.id, 6, 0, h_text])
            to_his([request.user, 5, d_p.id, 6, 0, h_text])

        return HttpResponseRedirect(f"../../?sel={s_port_id}")

    return render(request, 'del_ext.html', {'s_p': s_p, 'd_p': d_p,})


@login_required(login_url='/core/login/')
def int_c(request, bu_id, lo_id, s_id, s_port_id, s_type):

    if not request.user.has_perm("core.can_int"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    cr, dev, box = [], [], []

    if s_type in ('1', '2'):
        cr = Cross.objects.filter(parrent_id=lo_id).order_by('name').values('id', 'name', 'v_forw_l_r', 'v_row', 'v_col')
        if cr.exists():
            for cr_ob in cr:
                cr_ob_p = Cross_ports.objects.filter(parrent_id=cr_ob['id'])#.order_by('num')
                cr_p_h = []
                v_row = cr_ob['v_col']
                v_col = cr_ob['v_row']
                if cr_ob['v_forw_l_r']:
                    v_row, v_col = v_col, v_row
                p_count = 0
                for _ in range(v_row):
                    cr_p_v = []
                    for _ in range(v_col):
                        p_count += 1
                        curr_p = cr_ob_p.get(num=p_count)
                        cr_p_v.append((curr_p.id,                               #0
                                       curr_p.num,                              #1
                                       curr_p.int_c_status,                     #2
                                       curr_p.p_valid,                          #3
                                       curr_p.prim                              #4
                                       ))
                    cr_p_h.append(cr_p_v)

                if not cr_ob['v_forw_l_r']:
                    cr_p_h = zip(*cr_p_h)
                cr_ob['cr_p'] = cr_p_h

    if s_type in ('1', '2', '3'):
        dev = Device.objects.filter(parrent_id=lo_id).order_by('obj_type__parrent_id', 'name')\
                            .values('id', 'name', 'ip_addr', 'obj_type__parrent_id')
        for dev_ob in dev:
            dev_ob['dev_p'] = Device_ports.objects.filter(parrent_id=dev_ob['id']).order_by('num', 'id')\
                                          .values('id', 'num', 'int_c_status', 'p_valid', 'p_alias', 'prim')

    if s_type == '2':
        box = Box.objects.filter(parrent_id=lo_id).order_by('name', 'num').values('id', 'name', 'num', 'name_type')
        for box_ob in box:
            box_ob_p = Box_ports.objects.filter(parrent_id=box_ob['id']).order_by('num')\
                                        .values('id', 'up_status', 'p_valid', 'p_alias', 'dogovor', 'ab_kv')
            for ob in box_ob_p:
                ob['pair'] = ob['p_alias'][3:-1]
                ob['plint'] = int(ob['p_alias'][:1] if (ob['p_alias'][:1].isdigit()) else '0')
            box_ob['box_p'] = box_ob_p

    int_type_list = conf.MODELS_LIST[1:5]
    s_p_id = eval(f"{int_type_list[int(s_type)]}_ports").objects.get(pk=s_port_id)
    s_p_title = (s_p_id.parrent.parrent.parrent.name,
                 s_p_id.parrent.parrent.parrent.house_num,
                 s_p_id.parrent.parrent.name,
                 s_p_id.parrent.name,
                 s_p_id.parrent.num if s_type == '3' else s_p_id.num,
                 s_p_id.p_alias if s_type == '3' else ''
                 )

    return render(request, 'int_cr.html', {
                                          's_type': s_type,
                                          'cr': cr,
                                          'dev': dev,
                                          'box': box,
                                          's_p_title': s_p_title
                                          })


@login_required(login_url='/core/login/')
def int_ok(request, bu_id, lo_id, s_id, s_port_id, s_type, d_port_id, d_type):

    if not request.user.has_perm("core.can_int"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    int_type_list = conf.MODELS_LIST[1:5]
    tab_list = (None, 'Cross_ports', 'Device_ports', 'Box_ports')
    s_p = eval(tab_list[int(s_type)]).objects.get(pk=s_port_id)
    d_p = eval(tab_list[int(d_type)]).objects.get(pk=d_port_id)
    # if s_type == '1':   s_p = Cross_ports.objects.get(pk=s_port_id)
    # if s_type == '2':   s_p = Device_ports.objects.get(pk=s_port_id)
    # if s_type == '3':   s_p = Box_ports.objects.get(pk=s_port_id)
    # if d_type == '1':   d_p = Cross_ports.objects.get(pk=d_port_id)
    # if d_type == '2':   d_p = Device_ports.objects.get(pk=d_port_id)
    # if d_type == '3':   d_p = Box_ports.objects.get(pk=d_port_id)
    if s_port_id == d_port_id and s_type == d_type:
        return HttpResponseRedirect('../../')

    if request.method == 'POST':
        form = sel_up_status_Form(request.POST)
        if form.is_valid():
            sel_status = form.cleaned_data['status']
            with transaction.atomic():
                h_text = f'УД: {s_p.parrent.parrent.name}; {int_type_list[int(s_type)]}_id-{s_p.parrent.id} p_id-{s_p.id}'
                h_text += f' >>> {int_type_list[int(d_type)]}_id-{d_p.parrent.id} p_id-{d_p.id}'
                if s_type == '1':
                    if s_p.int_c_status != 0:
                        return render(request, 'error.html', {'mess': 's_p.int_c_status != 0', 'back': 2})
                    s_p.int_c_dest = d_type
                    s_p.int_c_id = d_port_id
                    s_p.int_c_status = sel_status
                    to_his([request.user, 5, s_p.id, 4, 0, h_text])
                if s_type == '2':
                    if s_p.int_c_status != 0:
                        return render(request, 'error.html', {'mess': 's_p.int_c_status != 0', 'back': 2})
                    s_p.int_c_dest = d_type
                    s_p.int_c_id = d_port_id
                    s_p.int_c_status = sel_status
                    to_his([request.user, 6, s_p.id, 4, 0, h_text])
                if s_type == '3':
                    if s_p.up_status != 0:
                        return render(request, 'error.html', {'mess': 's_p.up_status != 0', 'back': 2})
                    s_p.up_device_id = d_port_id
                    s_p.up_status = sel_status
                    to_his([request.user, 7, s_p.id, 4, 0, h_text])
                if d_type == '1':
                    if d_p.int_c_status != 0:
                        return render(request, 'error.html', {'mess': 'd_p.int_c_status != 0', 'back': 2})
                    d_p.int_c_dest = s_type
                    d_p.int_c_id = s_port_id
                    d_p.int_c_status = sel_status
                    to_his([request.user, 5, d_p.id, 4, 0, h_text])
                if d_type == '2':
                    if d_p.int_c_status != 0:
                        return render(request, 'error.html', {'mess': 'd_p.int_c_status != 0', 'back': 2})
                    d_p.int_c_dest = s_type
                    d_p.int_c_id = s_port_id
                    d_p.int_c_status = sel_status
                    to_his([request.user, 6, d_p.id, 4, 0, h_text])
                if d_type == '3':
                    if d_p.up_status != 0:
                        return render(request, 'error.html', {'mess': 'd_p.up_status != 0', 'back': 2})
                    d_p.up_device_id = s_port_id
                    d_p.up_status = sel_status
                    to_his([request.user, 7, d_p.id, 4, 0, h_text])
                s_p.save()
                d_p.save()

            return HttpResponseRedirect(f"../../../../?sel={s_port_id}")
    else:
        form = sel_up_status_Form(initial={'status': 1})

    return render(request, 'int_sel_status.html', {'s_p': s_p,
                                                   'd_p': d_p,
                                                   's_type': s_type,
                                                   'd_type': d_type,
                                                   'form': form,
                                                   })


@login_required(login_url='/core/login/')
def del_int_c(request, bu_id, lo_id, s_id, s_port_id, s_type):

    if not request.user.has_perm("core.can_int"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    if request.method == 'POST':
        int_type_list = conf.MODELS_LIST[1:5]
        with transaction.atomic():
            if s_type == '1':
                s_p = Cross_ports.objects.get(pk=s_port_id)
                if s_p.int_c_status == 0:
                    return render(request, 'error.html', {'mess': 's_p.int_c_status == 0', 'back': 2})
                d_port_id = s_p.int_c_id
                d_type = s_p.int_c_dest
            if s_type == '2':
                s_p = Device_ports.objects.get(pk=s_port_id)
                if s_p.int_c_status == 0:
                    return render(request, 'error.html', {'mess': 's_p.int_c_status == 0', 'back': 2})
                d_port_id = s_p.int_c_id
                d_type = s_p.int_c_dest
            if s_type == '3':
                s_p = Box_ports.objects.get(pk=s_port_id)
                if s_p.up_status == 0:
                    return render(request, 'error.html', {'mess': 's_p.up_status == 0', 'back': 2})
                d_port_id = s_p.up_device_id
                d_type = 2

            if d_type in (1, '1'):
                d_p = Cross_ports.objects.get(pk=d_port_id)
                if d_p.int_c_status == 0:
                    return render(request, 'error.html', {'mess': 'd_p.int_c_status == 0', 'back': 2})
            if d_type in (2, '2'):
                d_p = Device_ports.objects.get(pk=d_port_id)
                if d_p.int_c_status == 0:
                    return render(request, 'error.html', {'mess': 'd_p.int_c_status == 0', 'back': 2})
            if d_type in (3, '3'):
                d_p = Box_ports.objects.get(pk=d_port_id)
                if d_p.up_status == 0:
                    return render(request, 'error.html', {'mess': 'd_p.up_status == 0', 'back': 2})

            h_text = f'УД: {s_p.parrent.parrent.name}; {int_type_list[int(s_type)]}_id-{s_p.parrent.id} p_id-{s_p.id}'
            h_text += f' >>> {int_type_list[int(d_type)]}_id-{d_p.parrent.id} p_id-{d_p.id}'
            if s_type == '1':
                s_p.int_c_dest = 0
                s_p.int_c_id = 0
                s_p.int_c_status = 0
                to_his([request.user, 5, s_p.id, 7, 0, h_text])
            if s_type == '2':
                s_p.int_c_dest = 0
                s_p.int_c_id = 0
                s_p.int_c_status = 0
                to_his([request.user, 6, s_p.id, 7, 0, h_text])
            if s_type == '3':
                s_p.up_device_id = 0
                s_p.up_status = 0
                to_his([request.user, 7, s_p.id, 7, 0, h_text])
            if d_type == 1:
                d_p.int_c_dest = 0
                d_p.int_c_id = 0
                d_p.int_c_status = 0
                to_his([request.user, 5, d_p.id, 7, 0, h_text])
            if d_type == 2:
                d_p.int_c_dest = 0
                d_p.int_c_id = 0
                d_p.int_c_status = 0
                to_his([request.user, 6, d_p.id, 7, 0, h_text])
            if d_type == 3:
                d_p.up_device_id = 0
                d_p.up_status = 0
                to_his([request.user, 7, d_p.id, 7, 0, h_text])
            s_p.save()
            d_p.save()

        return HttpResponseRedirect(f"../../?sel={s_port_id}")

    lo = Locker.objects.get(pk=lo_id)

    return render(request, 'del_int.html', {'lo': lo})


@login_required(login_url='/core/login/')
def cr_ab(request, bu_id, lo_id, box_id, port_id):

    if not request.user.has_perm("core.can_ab"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    bu = Building.objects.get(pk=bu_id)
    kv = Kvartal.objects.get(pk=bu.kvar)
    lo = Locker.objects.get(pk=lo_id)
    cl_val = False
    n_port_id = 0
    cur_dev_p = 0                               #по умолчанию свободных портов нет
    txt_p, txt_l = '', ''
    # подготовка списка коммутов с портами для отображения
    dev_list = Device.objects.filter(parrent_id=lo_id).order_by('id')
    if dev_list.count() == 0:
        return render(request, 'error.html', {'mess': 'нет активного оборудования', 'back': 2})
    else:
        dev_p_cl = []
        # cr_text = ''
        ind_col = 0
        for dev_ob in dev_list:
            dev_ob_p = Device_ports.objects.filter(parrent_id=dev_ob.id).order_by('num', 'id')
            dev_p_cl2 = []
            for ob in dev_ob_p:
                dis = True                      #disable radio-button
                cr_text = ''
                if not ob.p_valid:
                    cr_text += ' неисправный '
                    ind_col = 5
                elif ob.int_c_status == 0:
                    dis = False
                    cr_text += ' свободный '
                    if not cl_val:
                        n_port_id = ob.id
                        cl_val = True
                    ind_col = 0
                elif ob.int_c_dest == 3:
                    b_p = Box_ports.objects.get(pk=ob.int_c_id)
                    if b_p.int_c_status == 0:
                        dis = False
                        cr_text += f"{b_p.parrent.name}-{b_p.parrent.num}-{b_p.p_alias}"
                        if len(b_p.his_dogovor) > 4:
                            cr_text += f" была:{b_p.his_ab_kv}кв{b_p.his_dogovor}"
                        else:
                            cr_text += ' скроссировано '
                        ind_col = 0
                    if b_p.int_c_status == 1 or b_p.int_c_status == 3:
                        dis = True
                        cr_text += f"{b_p.parrent.name}-{b_p.parrent.num}-{b_p.p_alias} занят:{b_p.ab_kv}кв{b_p.dogovor}"
                        ind_col = 1
                    if b_p.int_c_status == 2:
                        dis = True
                        cr_text += f"{b_p.parrent.name}-{b_p.parrent.num}-{b_p.p_alias} бронь:{b_p.ab_kv}кв{b_p.dogovor}"
                        ind_col = 2
                else:
                    cr_text += ' занят '
                    ind_col = 4
                dev_p_cl2.append({'id': ob.id,
                                  'num': ob.num,
                                  'p_valid': ob.p_valid,
                                  'dis': dis,
                                  'cr_text': cr_text,
                                  'col2': str(ind_col)
                                  })
            dev_p_cl.append(dev_p_cl2)

    cur_box_p = Box_ports.objects.get(pk=port_id)
    ch_port = ''
    # принятие данных с формы
    if request.method == 'POST':
        form = cr_ab_Form(request.POST)
        ch_port = request.POST['ch_port']
        if ch_port == '0':                          #если новый порт не выбран
            cur_dev_id = int(request.POST['c_port'])
            if cur_dev_id != 0:                     #не найден порт по умолчанию
                dog = form.data['dog'].strip()
                if len(dog) != 0:
                    sel_status = int(form.data['status'])
                    kvar = form.data['kvar']
                    fio = form.data['fio']
                    prim = form.data['prim']
                    prim_l = str(request.POST['prim_2'])

                    with transaction.atomic():
                        if cur_box_p.int_c_status != 0:     #уже не свободный
                            return render(request, 'error.html', {'mess': 'порт уже занят', 'back': 2})
                        if cur_box_p.up_device_id == cur_dev_id:
                            #if cur_box_p.up_status != 2:
                            #    pass    #txt_p = 'п:кросс '
                            if Device_ports.objects.get(pk=cur_dev_id).p_valid == False:
                                return render(request, 'error.html', {'mess': 'порт скроссирован, но помечен как неисправный', 'back': 2})
                        else:
                            if cur_box_p.up_status != 0:    #скроссирован не тот порт -> снять
                                del_p = Device_ports.objects.get(pk=cur_box_p.up_device_id)
                                if del_p.int_c_status == 0 or del_p.int_c_dest != 3:
                                    return render(request, 'error.html',
                                                  {'mess': 'crab1 -> del_p.int_c_status == 0 or del_p.int_c_dest != 3', 'back': 2})
                                del_p.int_c_dest = 0
                                del_p.int_c_id = 0
                                del_p.int_c_status = 0
                                cur_box_p.up_device_id = 0
                                cur_box_p.up_status = 0
                                del_p.save()
                                cur_box_p.save()
                                to_his([request.user, 7, cur_box_p.id, 7, 0,
                                        f"cr_ab (скроссирован другой порт -> снимаем {del_p.parrent.name} p-{del_p.num}) ВНИМАНИЕ !!!"])
                                to_his([request.user, 6, del_p.id, 7, 0, 'cr_ab (скроссирован другой порт -> снять) ВНИМАНИЕ !!!'])
                            if cur_box_p.up_status != 0:
                                return render(request, 'error.html', {'mess': 'crab2 -> cur_box_p.up_status != 0', 'back': 2})
                            new_d_p = Device_ports.objects.get(pk=cur_dev_id)
                            #освободить новый порт и взять историю
                            if new_d_p.int_c_status != 0:
                                if new_d_p.int_c_dest == 1 or new_d_p.int_c_dest == 2:
                                    return render(request, 'error.html',
                                                  {'mess': 'crab3 -> new_d_p.int_c_dest == 1 or new_d_p.int_c_dest == 2', 'back': 2})
                                new_d_p_box = Box_ports.objects.get(pk=new_d_p.int_c_id)
                                if new_d_p_box.int_c_status != 0:
                                    return render(request, 'error.html',
                                                  {'mess': 'crab4 -> new_d_p_box.int_c_status != 0', 'back': 2})
                                new_d_p_box.up_device_id = 0
                                new_d_p_box.up_status = 0
                                new_d_p.int_c_dest = 0
                                new_d_p.int_c_id = 0
                                new_d_p.int_c_status = 0
                                new_d_p_box.save()
                                new_d_p.save()
                                to_his([request.user, 6, new_d_p.id, 7, 0, 'cr_ab (освободить новый порт и взять историю)'])
                                to_his([request.user, 7, new_d_p_box.id, 7, 0, 'cr_ab (освободить новый порт и взять историю)'])
                            if new_d_p.int_c_status != 0:
                                return render(request, 'error.html', {'mess': 'crab5 -> new_d_p.int_c_status != 0', 'back': 2})
                            #кроссируем новый порт
                            new_d_p.int_c_dest = 3
                            new_d_p.int_c_id = port_id
                            new_d_p.int_c_status = sel_status
                            cur_box_p.up_device_id = cur_dev_id
                            cur_box_p.up_status = sel_status
                            new_d_p.save()
                            cur_box_p.save()
                            to_his([request.user, 6, new_d_p.id, 4, 0, 'cr_ab (кроссируем новый порт)'])
                            to_his([request.user, 7, cur_box_p.id, 4, 0, 'cr_ab (кроссируем новый порт)'])
                        #порт готов...
                        if sel_status != 2:
                            cur_box_p.up_status = sel_status
                        cur_box_p.int_c_status = sel_status
                        cur_box_p.dogovor = dog
                        cur_box_p.ab_kv = kvar
                        cur_box_p.ab_fio = fio
                        cur_box_p.ab_prim = f"{prim_l} / {prim}"
                        cur_box_p.date_cr = datetime.datetime.now()
                        cur_box_p.save()
                        h_text = f'cr_ab УД: {cur_box_p.parrent.parrent.name}; крт: {cur_box_p.parrent.name}-{cur_box_p.parrent.num}-{cur_box_p.p_alias}'
                        h_text += f'; {cur_box_p.dogovor} || {cur_box_p.ab_kv} || {cur_box_p.ab_fio} || {cur_box_p.ab_prim}'
                        to_his([request.user, 7, cur_box_p.id, 5, 0, h_text])

                    return HttpResponseRedirect('../../')
    # перерисовка формы с другим портом
        else:
            cur_dev_id = ch_port

        form = cr_ab_Form(initial={'dog': form.data['dog'],
                                   'kvar': form.data['kvar'],
                                   'fio': form.data['fio'],
                                   'prim': form.data['prim'],
                                   'status': form.data['status']
                                   })
    # новая прорисовка формы
    else:
        try:
            init_form = {'dog': request.GET['dog'],
                         'kvar': request.GET['kv'],
                         'fio': request.GET['fio'],
                         'status': 2
                         }
        except:
            init_form = {'status': 2}
        form = cr_ab_Form(initial=init_form)

        if cur_box_p.up_status != 0:
            cur_dev_id = Device_ports.objects.get(pk=cur_box_p.up_device_id).id
        else:
            cur_dev_id = n_port_id
    # подготовка строки примечания
    if cur_dev_id in (0, '0'):
        pass
    else:
        cur_dev_p = Device_ports.objects.get(pk=cur_dev_id)
        # история линейных данных
        if cur_dev_p.int_c_status != 0 and cur_dev_p.int_c_dest == 3:
            if cur_dev_p.int_c_id == cur_box_p.id:
                if cur_box_p.up_status != 2:
                    txt_p = 'п:скросс.'
            else:
                cur_dev_p_box = Box_ports.objects.get(pk=cur_dev_p.int_c_id)
                if len(cur_dev_p_box.his_dogovor) > 4:
                    if len(cur_dev_p_box.his_ab_kv) >= 1:
                        txt_p = 'п:'+cur_dev_p_box.his_ab_kv+'кв'+cur_dev_p_box.his_dogovor+'{'+cur_dev_p_box.parrent.name+'-'+cur_dev_p_box.parrent.num+'-'+cur_dev_p_box.p_alias
                    else:
                        txt_p = 'п:'+cur_dev_p_box.his_dogovor+'{'+cur_dev_p_box.parrent.name+'-'+cur_dev_p_box.parrent.num+'-'+cur_dev_p_box.p_alias
                else:
                    txt_p = 'п:'+'{'+cur_dev_p_box.parrent.name+'-'+cur_dev_p_box.parrent.num+'-'+cur_dev_p_box.p_alias
                txt_p += '}'+'.'+str(cur_dev_p_box.id)+'.~ '

        if len(cur_box_p.his_dogovor) > 4:
            if len(cur_box_p.his_ab_kv) >= 1:
                txt_l = f' л:{cur_box_p.his_ab_kv}кв{cur_box_p.his_dogovor}'
            else:
                txt_l = f' л:{cur_box_p.his_dogovor}'

    return render(request, 'cr_ab.html', {'bu': bu,
                                          'kv': kv,
                                          'lo': lo,
                                          'cur_box_p': cur_box_p,
                                          'form': form,
                                          'txt_p': txt_p,
                                          'txt_l': txt_l,
                                          'cur_dev_id': cur_dev_id,
                                          'cur_dev_p': cur_dev_p,
                                          'dev_list': dev_list,
                                          'dev_p_cl': dev_p_cl,
                                          })


@login_required(login_url='/core/login/')
def del_ab(request, bu_id, lo_id, box_id, port_id, pri):

    if not request.user.has_perm("core.can_ab"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    back_p = None
    back_p_id = ''
    d_p = 0
    s_p = Box_ports.objects.get(pk=port_id)
    no_kv = True if (s_p.ab_kv == '') else False
    if s_p.up_status == 2:
        d_p = Device_ports.objects.get(pk=s_p.up_device_id)
        if re.search(r'{.+}', s_p.ab_prim):
            back_p = re.search(r'{.+}', s_p.ab_prim).group(0)[1:-1]
            back_p_id = re.search(r'}.+\.', s_p.ab_prim).group(0)[2:-1]

    if request.method == 'POST':
        form = del_ab_Form(request.POST)
        if form.is_valid():
            sel_pri = form.data['pri']
            with transaction.atomic():
                if s_p.int_c_status == 0:
                    return render(request, 'error.html', {'mess': 'error: s_p.int_c_status == 0', 'back': 2})
                if s_p.int_c_status != 2:
                    s_p.his_dogovor = s_p.dogovor
                    s_p.his_ab_kv = s_p.ab_kv
                    s_p.his_ab_fio = s_p.ab_fio
                    s_p.his_ab_prim = s_p.ab_prim+conf.PRI_LIST[int(sel_pri)]
                    s_p.date_del = datetime.datetime.now()
                if s_p.int_c_status == 3 and s_p.dogovor.find('_su_') != -1:
                    try:
                        su = Subunit.objects.get(pk=s_p.dogovor.replace('_su_', ''), box_p_id=s_p.id)
                        su.box_p_id = 0
                        su.save()
                        h_text = f'del_ab УД: {s_p.parrent.parrent.name}; крт: {s_p.parrent.name}-{s_p.parrent.num}-{s_p.p_alias}'
                        h_text += f'; his: {s_p.his_dogovor} || {s_p.his_ab_kv} || {s_p.his_ab_fio} || {s_p.his_ab_prim}'
                        to_his([request.user, 13, su.id, 8, int(sel_pri), h_text])
                        no_kv = False
                    except:
                        pass
                if s_p.up_status == 2:
                    d_p = Device_ports.objects.get(pk=s_p.up_device_id)
                    if d_p.int_c_status != 2:
                        return render(request, 'error.html', {'mess': 'error: d_p.int_c_status != 2', 'back': 2})
                    d_p.int_c_dest = 0
                    d_p.int_c_id = 0
                    d_p.int_c_status = 0
                    # возврат порта на старые пары, если не занято
                    if back_p_id.isdigit():
                        back = Box_ports.objects.get(pk=int(back_p_id))
                        if back.up_status == 0:
                            back.up_status = 1
                            back.up_device_id = d_p.id
                            d_p.int_c_dest = 3
                            d_p.int_c_id = back.id
                            d_p.int_c_status = 1
                            back.save()
                            to_his([request.user, 6, d_p.id, 4, 0, 'del_ab (возврат порта на старые пары)'])
                            to_his([request.user, 7, back.id, 4, 0, 'del_ab (возврат порта на старые пары)'])

                    d_p.save()
                    to_his([request.user, 6, d_p.id, 7, 0, 'del_ab (бронь -> снимаем кроссировку)'])
                    to_his([request.user, 7, s_p.id, 7, 0, 'del_ab (бронь -> снимаем кроссировку)'])
                    s_p.up_device_id = 0
                    s_p.up_status = 0
                s_p.int_c_status = 0
                s_p.dogovor = ''
                s_p.ab_kv = ''
                s_p.ab_fio = ''
                s_p.ab_prim = ''

            s_p.save()
            h_text = f'del_ab УД: {s_p.parrent.parrent.name}; крт: {s_p.parrent.name}-{s_p.parrent.num}-{s_p.p_alias}'
            h_text += f'; his: {s_p.his_dogovor} || {s_p.his_ab_kv} || {s_p.his_ab_fio} || {s_p.his_ab_prim}'
            to_his([request.user, 7, s_p.id, 8, int(sel_pri), h_text])

            if no_kv:
                return HttpResponseRedirect(f'../../p_edit={port_id}')
            return HttpResponseRedirect(f'../../?sel={port_id}')
    else:
        form = del_ab_Form(initial={'pri': pri})

    return render(request, 'del_ab.html', {'s_p': s_p,
                                           'd_p': d_p,
                                           'form': form,
                                           'back_p': back_p,
                                           'no_kv': no_kv,
                                           })


@login_required(login_url='/core/login/')
def cr_su(request, bu_id, lo_id, box_id, port_id, su_id):

    if not request.user.has_perm("core.can_ab"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    bu = Building.objects.get(pk=bu_id)
    kv = Kvartal.objects.get(pk=bu.kvar)
    lo = Locker.objects.get(pk=lo_id)
    box_p = Box_ports.objects.get(pk=port_id)

    if su_id != '0':
        su = Subunit.objects.get(pk=int(su_id))
        if su.parrent_id != lo.id:
            return render(request, 'error.html', {'mess': 'error: su.parrent_id != lo.id', 'back': 2})
        #if box_p.int_c_status != 0:
        #    return render(request, 'error.html', {'mess': 'error_044', 'back': 2})
        with transaction.atomic():
            if box_p.int_c_status != 0:
                return render(request, 'error.html', {'mess': 'error: box_p.int_c_status != 0', 'back': 2})
            su.box_p_id = port_id
            box_p.int_c_status = 3
            box_p.dogovor = f'_su_{su.id}'
            box_p.ab_fio = su.name
            box_p.date_cr = datetime.datetime.now()

            su.save()
            box_p.save()

            h_text = f'cr_su УД: {lo.name}; крт: {box_p.parrent.name}-{box_p.parrent.num}-{box_p.p_alias}; {box_p.dogovor} || {box_p.ab_fio}'
            to_his([request.user, 7, box_p.id, 5, 0, h_text])
            to_his([request.user, 13, su.id, 5, 0, h_text])

        return HttpResponseRedirect('../../')

    su_list = Subunit.objects.filter(parrent_id=lo_id).order_by('con_type', 'name').values()
    if su_list.count() != 0:
        for ob in su_list:
            ob['name_type'] = Templ_subunit.objects.get(pk=ob['con_type'])#conf.SUBUNIT_TYPE[ob['con_type']][1]

    return render(request, 'cr_su.html', {'bu': bu,
                                          'kv': kv,
                                          'lo': lo,
                                          'cur_box_p': box_p,
                                          'su_list': su_list,
                                          })

