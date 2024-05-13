# cross__views

import datetime

from django.contrib.auth.decorators import login_required
# from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
# from django.http import HttpResponse
# from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Kvartal, Building, Locker, Cross, Device, Box, Subunit
from .models import Cross_ports, Device_ports, Device_ports_v, Box_ports
from core.models import Templ_cross, Templ_device, Templ_box_cable, Templ_box, Templ_subunit
from core.models import Subunit_type, manage_comp, History
from cable.models import Coupling

from .forms import energy_Form, edit_racks_Form

from core.shared_def import chain_trace, upd_visit, to_his#, from_bgb_gog_rq
from core.e_config import conf

####################################################################################################

@login_required(login_url='/core/login/')
def show_bu_lo(request, bu_id, lo_id=0):

    upd_visit(request.user, f'sh_bu_{bu_id}_{lo_id}')
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id, parrent_id=bu_id).get_dict() if lo_id else {}
    except ObjectDoesNotExist as error:
        return render(request, 'error.html', {'mess': f'объект не найден ({error})', 'back': 8})

    if lo and lo['agr'] and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1,
                                               'next_url': f"/cross/build={bu_id}/locker={lo_id}/"
                                               })

    jyr_info = check_deadline(bu) if not lo_id else False
    bu_double = False
    try:
        if bu.double_id != 0:
            bu_double = (True, Building.objects.get(pk=bu.double_id))
    except ObjectDoesNotExist:
        bu_double = (False, None)

    lo_list = Locker.objects.filter(parrent_id=bu_id).exclude(pk=lo_id).values().order_by('-agr', 'name')
    #lo_list = Locker.objects.filter(parrent_id=bu_id).values().order_by('-agr', 'name')
    lo_obj = (False,) * 4
    for ob in lo_list:
        ob['status2'] = conf.STATUS_LIST_LO[ob['status']]
        ob['coup_id'] = Coupling.objects.get(parrent=ob['id'], parr_type=0).id
    if lo:
        lo['status2'] = conf.STATUS_LIST_LO[lo['status']]
        lo['coup_id'] = Coupling.objects.get(parrent=lo['id'], parr_type=0).id

        cross_list = Cross.objects.filter(parrent_id=lo_id).order_by('name')\
            .values('id', 'name', 'name_type', 'prim', 'object_owner')
        device_list = Device.objects.filter(parrent_id=lo_id).order_by('obj_type__parrent_id', 'name')\
            .values('id', 'name', 'obj_type__name', 'ip_addr', 'prim', 'ip_mask', 'ip_gateway', 'vlan', \
                    'object_owner', 'obj_type__parrent_id', 'obj_type__parrent__name')
        box_list = Box.objects.filter(parrent_id=lo_id).order_by('name', 'num').values()
        subunit_list = Subunit.objects.filter(parrent_id=lo_id).order_by('name').values()
        repack_su(subunit_list, lo_id)

        lo_obj = (cross_list, device_list, box_list, subunit_list)

    return render(request, 'show_build_locker.html',   {'bu': bu,
                                                        'kv': kv,
                                                        'lo': lo,
                                                        'lo_id': int(lo_id),
                                                        'lo_list': lo_list,
                                                        'lo_obj': lo_obj,
                                                        'bu_double': bu_double,
                                                        'jyr_info': jyr_info,
                                                        })
# if (request.user.groups.filter(name='test').exists())
####################################################################################################

def repack_su(subunit_list, lo_id):
    for ob in subunit_list:
        name_type = Templ_subunit.objects.get(pk=ob['con_type'])
        ob['info'] = (name_type.name,
                      name_type.parrent_id,
                      name_type.parrent.name,
                      conf.POE_TYPE[ob['poe']][1]
                      )
        if ob['box_p_id'] == 0:
            ob['box'] = ''
        else:
            try:
                ob['box'] = Box_ports.objects.get(\
                    pk=ob['box_p_id'], parrent__parrent_id=lo_id, int_c_status=3, dogovor=f"_su_{ob['id']}")
            except ObjectDoesNotExist:
                ob['box'] = ''
                su = Subunit.objects.get(pk=ob['id'])
                su.box_p_id = 0
                su.save()


def check_deadline(bu):
    try:
        upr_comp = manage_comp.objects.get(pk=bu.info_comp)
    except ObjectDoesNotExist:
        upr_comp = {'name': 'нет информации', 'info': ''}
    try:
        alert = False
        m_delta = 3
        m_alert = []
        m_today = datetime.date.today().month
        d_today = datetime.date.today().day
        step = 0
        while step < m_delta:
            step += 1
            m_in = m_today + step
            if m_in > 12:
                m_in -= 12
            m_alert.append(m_in)
        l_alert = m_alert[-1]
        m_plan = bu.deadline.month
        d_plan = bu.deadline.day
        if m_plan in m_alert:
            alert = True
            if (m_plan == l_alert) and (d_plan > d_today):
                alert = False
        elif (m_plan == m_today) and (d_plan >= d_today):
            alert = True
        deadline = [d_plan, conf.MONTHS[m_plan], alert]
    except:
        deadline = False

    return (upr_comp, deadline)

####################################################################################################

@login_required(login_url='/core/login/')
def show_cr(request, bu_id, lo_id, cr_id):
    
    upd_visit(request.user, 'sh_cr')
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id)
        cr = Cross.objects.get(pk=cr_id)
    except ObjectDoesNotExist as error:
        return render(request, 'error.html', {'mess': f'объект не найден ({error})', 'back': 2})
    try:
        coup = Coupling.objects.get(parrent=lo_id, parr_type=0)
    except ObjectDoesNotExist:
        coup = False

    if lo.parrent_id != bu.id or cr.parrent_id != lo.id:
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1,
                                               'next_url': f"/cross/build={bu_id}/locker={lo_id}/cr={cr_id}/"
                                               })

    cr_list = Cross.objects.filter(parrent_id=lo_id).values().order_by('name')
    cr_p_list = Cross_ports.objects.filter(parrent_id=cr.id).values().order_by('num')

    for ob in cr_p_list:
        if ob['up_status'] == 0:
            if ob['cab_p_id'] != 0:
                res = chain_trace(ob['id'], '1', transit=True)
                try:
                    if res[0] == 1: c_up = ('ext_coup', f"m: {res[1].parrent.name}")
                    if res[0] == 2: c_up = ('ext_coup', f"уд: {res[1].parrent.parrent.name}")
                except:
                    c_up = ()
            else:
                c_up = ()
            c_up_l = ''
        else:
            try:
                up = Cross_ports.objects.get(pk=ob['up_cross_id'])
                c_up = (up.parrent.parrent.parrent.name,            #0 улица
                        up.parrent.parrent.parrent.house_num,       #1 дом
                        up.parrent.parrent.name,                    #2 УД
                        up.parrent.name,                            #3 кросс
                        str(up.num),                                #4 порт
                        str(up.id)                                  #6 ид противоположного порта для маркера
                        )
                c_up_l = f"/cross/build={up.parrent.parrent.parrent.id}/locker={up.parrent.parrent.id}/cr={up.parrent.id}"
            except ObjectDoesNotExist:
                c_up = ('link_err',)
                c_up_l = ''

        if ob['int_c_status'] == 0:
            c_down = ('blank.png',)
        else:
            if ob['int_c_dest'] == 1:
                try:
                    down = Cross_ports.objects.get(pk=ob['int_c_id'])
                    c_down = ('cr2.png',                            #'кросс ',
                              down.parrent.name,                    #1 имя кросса
                              str(down.num),                        #2 порт
                              f'../cr={down.parrent_id}',           #4 ссылка на противоположное оборудование
                              str(down.id)                          #5 ид противоположного порта для маркера
                              )
                except ObjectDoesNotExist:
                    c_down = ('cr2.png', 'link_err')

            if ob['int_c_dest'] == 2:
                try:
                    down = Device_ports.objects.get(pk=ob['int_c_id'])
                    c_down = (f"dev_{down.parrent.obj_type.parrent_id}.png",    #'акт.обор. ',
                              down.parrent.name,                    #1 имя коммута
                              str(down.num),                        #2 порт
                              f'../dev={down.parrent_id}',          #4 ссылка на противоположное оборудование
                              str(down.id)                          #5 ид противоположного порта для маркера
                              )
                except ObjectDoesNotExist:
                    c_down = ('kom2.png', 'link_err')

        ob['c_up'] = c_up
        ob['c_up_l'] = c_up_l
        ob['c_down'] = c_down

    try:    sel = int(request.GET['sel'])
    except: sel = False

    try:    to_print = int(request.GET['to_print'])
    except: to_print = False

    return render(request, 'show_cross.html', { 'bu': bu,
                                                'kv': kv,
                                                'lo': lo,
                                                'cr_list': cr_list,
                                                'cr': cr,
                                                'cr_p_list': cr_p_list,
                                                'sel': sel,
                                                'to_print': to_print,
                                                'coup': coup,
                                                })

####################################################################################################

@login_required(login_url='/core/login/')
def show_dev(request, bu_id, lo_id, dev_id, l2=0):

    upd_visit(request.user, 'sh_dev')
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id)
        dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist as error:
        return render(request, 'error.html', {'mess': f'объект не найден ({error})', 'back': 2+int(l2)})

    if lo.parrent_id != bu.id or dev.parrent_id != lo.id:
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3+int(l2)})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1+int(l2),
                                               'next_url': f"/cross/build={bu_id}/locker={lo_id}/dev={dev_id}/"
                                               })

    dev_list = Device.objects.filter(parrent_id=lo_id).values().order_by('name')
    dev_p_list = Device_ports.objects.filter(parrent_id=dev.id).values().order_by('num')
    dev_p_v_list = Device_ports_v.objects.filter(parrent_id=dev.id).values().order_by('parrent_p', 'vlan_untag')

    for ob in dev_p_list:
        if ob['int_c_status'] == 0:
            c_down = ('blank.png',)
        else:
            if ob['int_c_dest'] == 1:
                try:
                    down = Cross_ports.objects.get(pk=ob['int_c_id'])
                    down_ext = False
                    if down.up_status:
                        ext_cr = Cross_ports.objects.get(pk=down.up_cross_id)
                        down_ext = ((ext_cr.parrent.parrent.parrent_id,
                                     ext_cr.parrent.parrent.parrent.name, ext_cr.parrent.parrent.parrent.house_num), # 0 bu
                                    (ext_cr.parrent.parrent_id, ext_cr.parrent.parrent.name),                        # 1 lo
                                    (ext_cr.parrent_id, ext_cr.parrent.name),                                        # 2 cr
                                    (ext_cr.id, ext_cr.num))                                                         # 3 cr_p
                    c_down = ('cr2.png',                            #'кросс ',
                              down.parrent.name,                    #1 имя кросса
                              str(down.num),                        #2 порт
                              False,                                #3 N/A
                              False,                                #4 N/A
                              False,                                #5 N/A
                              False,                                #6 N/A
                              f"../cr={down.parrent.id}",           #7 ссылка на противоположное оборудование
                              down_ext,                             #8 внешний кросс
                              down.up_status,                       #9 статус внешней связи
                              str(down.id)                          #10 ид противоположного порта для маркера
                              )
                except ObjectDoesNotExist:
                    c_down = ('cr2.png', 'link_err')

            if ob['int_c_dest'] == 2:
                try:
                    down = Device_ports.objects.get(pk=ob['int_c_id'])
                    c_down = (f"dev_{down.parrent.obj_type.parrent_id}.png",    #'акт.обор. ',
                              down.parrent.name,                                #1 имя коммута
                              down.p_alias,                                     #2 порт
                              False,                                            #3 N/A
                              False,                                            #4 N/A
                              False,                                            #5 N/A
                              False,                                            #6 N/A
                              f"../dev={down.parrent.id}",                      #7 ссылка на противоположное оборудование
                              False,                                            #8 N/A
                              False,                                            #9 только для внешней связи
                              str(down.id)                                      #10 ид противоположного порта для маркера
                              )
                except ObjectDoesNotExist:
                    c_down = ('kom2.png', 'link_err')

            if ob['int_c_dest'] == 3:
                try:
                    down = Box_ports.objects.get(pk=ob['int_c_id'])
                    c_down = ('rj45_2_1.png',                               #'КРТ ',
                              f"{down.parrent.name}-{down.parrent.num}",    #1 имя КРТ
                              down.p_alias,                                 #2 порт КРТ
                              (down.dogovor, down.ab_kv, down.ab_fio),      #3 договор,кв,ФИО
                              'billing' if down.int_c_status == 1 else '',  #4 статус аб.кроссировки для ссылки в билинг
                              (down.his_ab_kv+'кв' if down.his_ab_kv != '' else '') + down.his_dogovor,  #5 история пары
                              down.int_c_status,                            #6 статус абонентской кроссировки
                              f"../box={down.parrent.id}",                  #7 ссылка на противоположное оборудование
                              False,                                        #8 N/A
                              False,                                        #9 только для внешней связи
                              str(down.id)                                  #10 ид противоположного порта для маркера
                              )
                except ObjectDoesNotExist:
                    c_down = ('rj45_2_1.png', 'link_err')

        ob['c_down'] = c_down

        step = 40
        if len(ob['vlan_tag_list']) > step:
            try:
                str1 = ob['vlan_tag_list']
                cnt = 0
                while True:
                    pos = str1.find(',', cnt+step)
                    if pos == -1: break
                    str1 = f"{str1[:pos+1]} {str1[pos+1:]}"
                    cnt = pos + 1
                ob['vlan_tag_list'] = str1
            except:
                ob['vlan_tag_list'] = 'ошибка построения, сообщите разработчику'

    try:    sel = int(request.GET['sel'])
    except: sel = False
    try:
        gog = request.GET['bil_rq']
        bil_rq = from_bgb_gog_rq(gog)
    except:
        bil_rq = [False, False]
    try:
        td = datetime.datetime.now() - dev.date_upd
        tmin,tsec = divmod(td.seconds, 60)
        th, tmin = divmod(tmin, 60)
        upd_td = [td.days, "%02d:%02d:%02d" % (th, tmin, tsec)]
    except:
        upd_td = False

    context = {'bu': bu,
               'kv': kv,
               'lo': lo,
               'dev_list': dev_list,
               'dev': dev,
               'dev_p_list': dev_p_list,
               'sel': sel,
               'bil_rq': bil_rq,
               'upd_td': upd_td,
               'dev_p_v_list': dev_p_v_list,
               'dev_nav': 2 if l2 == '1' else 1
               }

    templ = 'show_dev_v.html' if (l2 == '1') else 'show_dev.html'

    return render(request, templ, context)

####################################################################################################

@login_required(login_url='/core/login/')
def show_dev_ips(request, bu_id, lo_id, dev_id):

    upd_visit(request.user, 'sh_ips')
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id)
        dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist as error:
        return render(request, 'error.html', {'mess': f'объект не найден ({error})', 'back': 3})

    if lo.parrent_id != int(bu_id) or dev.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 4})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2,
                                               'next_url': f"/cross/build={bu_id}/locker={lo_id}/dev={dev_id}/"
                                               })

    dev_vector = []                         # уникальный список устройств
    dev = Device.objects.get(pk=dev_id)
    dev_list = Device.objects.filter(parrent_id=lo_id).order_by('name')
    dev_p_list = Device_ports.objects.filter(parrent_id=dev.id).order_by('num')
    t_list2 = [False] * dev_p_list.count()  # 'корневые' линки
    t_list3 = []                            # 'паровозные' линки
###
###
    def add_total(obj):
        nonlocal dev_vector, t_list2, t_list3
        dev_vector.append(obj[3])
        if obj[1] == 0:
            t_list2[obj[0]-1][1] = obj
        else:
            obj0 = t_list2[obj[0]-1][0].copy()
            obj0[2] = obj[1]
            t_list3.append([obj0, obj])
###                             проверка на повторяющийся коммут
    def check_vector(dev_id):
        nonlocal dev_vector
        return dev_id in dev_vector
###
    def ch_cr(lev, p_id, p_up, num):
        cr_p = Cross_ports.objects.get(pk=p_id)
        #cr = Cross.objects.get(pk=cr_p.parrent_id)
        if cr_p.up_status != 0:
            cr_p_up = Cross_ports.objects.get(pk=cr_p.up_cross_id)
            if cr_p_up.int_c_dest == 1:
                ch_cr(lev, cr_p_up.int_c_id, p_up, num)
            elif cr_p_up.int_c_dest == 2:
                ch_dev(lev, cr_p_up.int_c_id, 1, p_up, num)
            elif lev == 0:
                add_total([num, lev, 0, 0, False])
        elif lev == 0:
            add_total([num, lev, 0, 0, False])
###
    def ch_dev(lev, p_id, type_c, p_up, num):
        dev_p = Device_ports.objects.get(pk=p_id)
        dev = Device.objects.get(pk=dev_p.parrent_id)
        #dev_type = Templ_device.objects.get(pk=dev.con_type).parrent_id
        dev_type = dev.obj_type.parrent_id
        loop = check_vector(dev.id)
        if dev_type in [8] and lev != 0: # poe не показывать во вложениях
            pass
        else:
            add_total([num,                         #0  номер основного порта
                       lev,                         #1  уровень в дереве
                       dev_type,                    #2  тип
                       dev.id,                      #3  для вектора
                       dev,                         #4
                       type_c,                      #5  тип кроссировки
                       p_up,                        #6  порт аплинка
                       dev_p.p_alias,               #7  порт кроссировки
                       loop, #dev_type in [2,3]     #8  петля
                       ])
        if dev.parrent.agr == False and dev_type in [2,3] and not loop:
            dev_p_list = Device_ports.objects.filter(parrent_id=dev.id).order_by('num').exclude(pk=p_id)
            for port in dev_p_list:
                if port.int_c_dest == 1:
                    ch_cr(lev+1, port.int_c_id, port.p_alias, num)
                if port.int_c_dest == 2:
                    ch_dev(lev+1, port.int_c_id, 2, port.p_alias, num)
###
###
    for port in dev_p_list:
        t_list2[port.num-1] = [[port.num, port.p_alias, 0, 1, port.p_valid, port.port_t_x], [False]]
        #if port.num not in[0]:####
        if port.int_c_dest == 1:
            ch_cr(0, port.int_c_id, port.p_alias, port.num)
        elif port.int_c_dest == 2:
            ch_dev(0, port.int_c_id, 2, port.p_alias, port.num)
        elif port.int_c_dest == 3:
            add_total([port.num, 0, 0, 0, 'KRT'])
        else:
            add_total([port.num, 0, 0, 0, False])

    t_list3.reverse()           # объединение линков
    for ob in t_list3:
        t_list2.insert(ob[0][0], [ob[0], ob[1]])

    pos = []
    ind = 0
    while ind < len(t_list2):   # вычисление rowspan
        t_list2[ind][1][3] = '&emsp;'*2*t_list2[ind][0][2]
        if t_list2[ind][0][2] == 0:
            pos = ind
        else:
            t_list2[ind][0][3] = False
            t_list2[pos][0][3] += 1
        ind +=1

    context = {'bu': bu,
               'kv': kv,
               'lo': lo,
               'dev_list': dev_list,
               'dev': dev,
               'total_list2': t_list2,
               'dev_nav': 3
               }

    return render(request, 'show_dev_ips.html', context)

####################################################################################################

@login_required(login_url='/core/login/')
def show_box(request, bu_id, lo_id, box_id):

    upd_visit(request.user, 'sh_box')
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id)
        box = Box.objects.get(pk=box_id)
    except ObjectDoesNotExist as error:
        return render(request, 'error.html', {'mess': f'объект не найден ({error})', 'back': 2})

    if lo.parrent_id != int(bu_id) or box.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1,
                                               'next_url': f"/cross/build={bu_id}/locker={lo_id}/box={box_id}/"
                                               })
    try:    select = int(request.GET['sel'])
    except: select = 0
    try:
        gog = request.GET['bil_rq']
        bil_rq = from_bgb_gog_rq(gog)
    except:
        bil_rq = [False, False]
    try:
        if bil_rq[0]:
            comm = bil_rq[0]['comment']
            kvar = comm.rsplit(' кв ')[1].rsplit(' ')[0]
            box_p = Box_ports.objects.get(pk=select)
            if box_p.ab_kv != kvar:
                h_text = f"УД: {box.parrent.name}; крт: {box.name}-{box.num}-{box_p.p_alias}; ab_kv: {box_p.ab_kv} -> {kvar}; "
                box_p.ab_kv = kvar
                box_p.save()
                to_his([request.user, 7, box_p.id, 17, 0, h_text])
    except:
        to_his([request.user, 4, box.id, 17, 0, f"error- {bil_rq[0]['comment']}"])

    box_list = Box.objects.filter(parrent_id=lo_id).values().order_by('name', 'num')
    box_p_list = Box_ports.objects.filter(parrent_id=box.id).values().order_by('num')
    templ_box_cab_list = Templ_box_cable.objects.all()
    i = 1
    cab_count = 1
    for ob in box_p_list:
        if ob['up_status'] == 0:
            c_up = []
            #l_up = ''###
        else:
            try:
                up = Device_ports.objects.get(pk=ob['up_device_id'])###
                c_up = ((up.parrent.id, up.parrent.name, up.parrent.ip_addr),
                        (str(up.id), str(up.num)))
                # c_up = (up.parrent.name,
                #         str(up.num),
                #         up.parrent.ip_addr,
                #         str(up.id)
                #         )
                #l_up = f"../dev={up.parrent.id}"###
            except ObjectDoesNotExist:
                c_up = ('link_err',)
                #l_up = ''

        plint = ob['p_alias'][:1]
        if not plint.isdigit():
            plint = '0'
        ob['pl_num'] = int(plint)
        ob['c_up'] = c_up
        #ob['l_up'] = l_up
        #ob['up_color'] = conf.COLOR_CROSS[ob['up_status']]###
        #ob['int_color'] = conf.COLOR_CROSS[ob['int_c_status']]###
        #ob['pl_color'] = conf.COLOR_PLINT[int(plint)]###
        ob['c_color'] = templ_box_cab_list.get(pk=int(ob['cable_id'])).color_cable
        
        i = i-1
        if i == 0:
            c_ports = templ_box_cab_list.get(pk=int(ob['cable_id'])).ports
            ob['c_ports1'] = c_ports * 2
            ob['c_ports2'] = cab_count
            ob['c_ports3'] = templ_box_cab_list.get(pk=int(ob['cable_id'])).name
            i = c_ports
            cab_count = cab_count + 1
        else:
            ob['c_ports1'] = False
            #ob['c_ports2'] = False

    return render(request, 'show_box.html', {'bu': bu,
                                             'kv': kv,
                                             'lo': lo,
                                             'box_list': box_list,
                                             'box': box,
                                             'box_p_list': box_p_list,
                                             'sel': select,
                                             'bil_rq': bil_rq,
                                             })


####################################################################################################

@login_required(login_url='/core/login/')
def energy(request, bu_id, lo_id):

    if not request.user.has_perm("core.can_edit_en"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})

    #bu = Building.objects.get(pk=bu_id)
    lo = Locker.objects.get(pk=lo_id)
    meter = lo.en_meter.split(',')

    if request.method == 'POST':
        form = energy_Form(request.POST)
        if form.is_valid():
            change = False
            h_text = 'УД (en): '+lo.name+'; '

            form_meter = form.cleaned_data['en_meter1'] + ',' + form.cleaned_data['en_meter2']
            if form_meter != lo.en_meter:
                change = True
                h_text += 'meter: '+lo.en_meter+' -> '+form_meter+'; '
                lo.en_meter = form_meter
            if form.cleaned_data['en_model'] != str(lo.en_model):
                change = True
                h_text += 'model: '+str(lo.en_model)+' -> '+str(form.cleaned_data['en_model'])+'; '
                lo.en_model = form.cleaned_data['en_model']
            if form.cleaned_data['en_sn'] != lo.en_sn:
                change = True
                h_text += 'sn: '+lo.en_sn+' -> '+form.cleaned_data['en_sn']+'; '
                lo.en_sn = form.cleaned_data['en_sn']
            try:
                date_reg = datetime.datetime.strptime(form.data['en_date_reg'], '%d.%m.%Y').date()
            except:
                date_reg = None
            if date_reg != lo.en_date_reg:
                change = True
                h_text += 'date_reg: '+str(lo.en_date_reg)+' -> '+str(date_reg)+'; '
                lo.en_date_reg = date_reg
            try:
                date_check = datetime.datetime.strptime(form.data['en_date_check'], '%d.%m.%Y').date()
            except:
                date_check = None
            if date_check != lo.en_date_check:
                change = True
                h_text += 'date_check: '+str(lo.en_date_check)+' -> '+str(date_check)+'; '
                lo.en_date_check = date_check

            if change:
                lo.save()
                to_his([request.user, 1, lo.id, 2, 0, h_text])
    else:
        form = energy_Form(initial={'en_model': lo.en_model,
                                    'en_sn': lo.en_sn,
                                    'en_meter1': meter[0],
                                    'en_meter2': meter[1],
                                    })

    en_his = History.objects.filter(obj_type=1, obj_id=lo.id, operation1=2).filter(text__startswith='УД (en):').order_by('-id')

    return render(request, 'energy.html', {'form': form,
                                           'lo': lo,
                                           'en_date_reg': lo.en_date_reg.strftime('%d.%m.%Y') if lo.en_date_reg != None else '',
                                           'en_date_check': lo.en_date_check.strftime('%d.%m.%Y') if lo.en_date_check != None else '',
                                           'en_his': en_his,
                                           })


####################################################################################################

@login_required(login_url='/core/login/')
def show_racks(request, bu_id, lo_id):

    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id)
    except ObjectDoesNotExist as error:
        return render(request, 'error.html', {'mess': f'объект не найден ({error})', 'back': 2})

    if lo.parrent_id != int(bu_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 2})
    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1,
                                               'next_url': f"/cross/build={bu_id}/locker={lo_id}/"
                                               })
    if request.method == 'POST':
        form = edit_racks_Form(request.POST)
        if form.is_valid():
            if form.cleaned_data['racks'] != lo.racks:
                if (len(form.cleaned_data['racks'].split(',')) % 2 == 0) or form.cleaned_data['racks'] == '':
                    lo.racks = form.cleaned_data['racks']
                    lo.save()
                    to_his([request.user, 1, lo.id, 2, 0, ''])
    else:
        form = edit_racks_Form(initial={'racks': lo.racks})

    upd_visit(request.user, 'sh_racks')

    cross_list = Cross.objects.filter(parrent_id=lo_id).order_by('name')#.values()
    device_list = Device.objects.filter(parrent_id=lo_id).order_by('name')#.values()
    box_list = Box.objects.filter(parrent_id=lo_id).order_by('name')#.values()

    rack_pos_list = lo.racks.split(',')
    rack_list = [['0', 1]]
    if len(rack_pos_list) > 1:
        i = 0
        while i < len(rack_pos_list) / 2:
            if not rack_pos_list[i*2+1].isdigit():
                return render(request, 'error.html', {'mess': 'ошибка в описании стоек', 'back': 1})
            rack_list.append([rack_pos_list[i*2], int(rack_pos_list[i*2+1])])
            i += 1

    for ob1 in rack_list:
        ind = rack_list.index(ob1)
        if ind:
            r_cr = cross_list.filter(rack_num=ind).exclude(rack_pos=0).values('id', 'name', 'rack_pos', 'con_type')
            #r_dev = device_list.filter(rack_num=ind).exclude(rack_pos=0).values('id', 'name', 'rack_pos', 'con_type')
            r_dev = device_list.filter(rack_num=ind).exclude(rack_pos=0)\
                .values('id', 'name', 'rack_pos', 'obj_type__parrent_id', 'obj_type__units')
            # print(r_dev)
            r_box = box_list.filter(rack_num=ind).exclude(rack_pos=0).values('id', 'name', 'rack_pos', 'con_type')
            cur_rack = []
            #i = 1
            i = ob1[1]
            while i > 0:
                if r_cr.filter(rack_pos=i).count() != 0:
                    cur_cr = r_cr.filter(rack_pos=i).first()
                    cur_units = Templ_cross.objects.get(pk=cur_cr['con_type']).units
                    #ports...
                    cur_rack.append([i, cur_cr, cur_units, 'laser2_1.png', 'cr='+str(cur_cr['id'])])
                    while cur_units > 1:
                        i -= 1
                        cur_rack.append([i, False, False, False, False])
                        cur_units -= 1
                elif r_dev.filter(rack_pos=i).count() != 0:
                    cur_dev = r_dev.filter(rack_pos=i).first()
                    #cur_units = Templ_device.objects.get(pk=cur_dev['con_type']).units
                    cur_units = cur_dev['obj_type__units']
                    #cur_type = Templ_device.objects.get(pk=cur_dev['con_type']).parrent_id
                    cur_type = cur_dev['obj_type__parrent_id']
                    #ports...
                    cur_rack.append([i, cur_dev, cur_units, 'dev_'+str(cur_type)+'.png', 'dev='+str(cur_dev['id'])])
                    while cur_units > 1:
                        i -= 1
                        cur_rack.append([i, False, False, False, False])
                        cur_units -= 1
                elif r_box.filter(rack_pos=i).count() != 0:
                    cur_box = r_box.filter(rack_pos=i).first()
                    cur_units = Templ_box.objects.get(pk=cur_box['con_type']).units
                    #ports...
                    cur_rack.append([i, cur_box, cur_units, 'rj45_2_1.png', 'box='+str(cur_box['id'])])
                    while cur_units > 1:
                        i -= 1
                        cur_rack.append([i, False, False])
                        cur_units -= 1
                else:
                    cur_rack.append([i, '', 1, False, False])
                i -= 1
            #cur_rack.reverse()
        else: # ['0', 1]
            r_cr = cross_list.filter(Q(rack_num=ind) | Q(rack_pos=0)).values('id', 'name', 'rack_pos', 'con_type')
            r_dev = device_list.filter(Q(rack_num=ind) | Q(rack_pos=0))\
                .values('id', 'name', 'rack_pos', 'rack_pos', 'obj_type__parrent_id', 'obj_type__units')
            cur_rack = []
            i = 1
            for cur_cr in r_cr:
                cur_rack.append([i, cur_cr, 1, 'laser2_1.png', 'cr='+str(cur_cr['id'])])
                i += 1
            for cur_dev in r_dev:
                #cur_type = Templ_device.objects.get(pk=cur_dev['con_type']).parrent_id
                cur_type = cur_dev['obj_type__parrent_id']
                cur_rack.append([i, cur_dev, 1, 'dev_'+str(cur_type)+'.png', 'dev='+str(cur_dev['id'])])
                i += 1

        ob1.append(cur_rack)
        #print('|')
        #print(cur_rack)
    #print('|||')
    #print(rack_list)
    return render(request, 'show_racks.html', {'bu': bu,
                                               'kv': kv,
                                               'lo': lo,
                                               'form': form,
                                               'rack_list': rack_list,
                                               'adm': request.user.has_perm("core.can_adm"),
                                               })
