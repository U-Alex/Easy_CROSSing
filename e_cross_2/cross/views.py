# cross__views

import datetime
#import re

from django.contrib.auth.decorators import login_required
#from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
#from django.db import transaction
from django.db.models import Q
#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Kvartal, Building, Locker, Cross, Device, Box, Subunit
from .models import Cross_ports, Device_ports, Device_ports_v, Box_ports
from core.models import Templ_cross, Templ_device, Templ_box_cable, Templ_box, Templ_subunit#, Templ_locker
from core.models import Subunit_type, manage_comp, History
from cable.models import Coupling

from .forms import energy_Form, edit_racks_Form

from core.shared_def import chain_trace, upd_visit, to_his#, from_bgb_gog_rq
from core.e_config import conf

####################################################################################################


@login_required(login_url='/core/login/')
def show_build(request, bu_id):
    
    upd_visit(request.user, 'sh_bu')
    bu_double = ''
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 1})
    
    locker_list = Locker.objects.filter(parrent_id=bu_id).values().order_by('-agr', 'name')
    
    if locker_list.count() != 0:
        for ob in locker_list:
            ob['status2'] = [conf.COLOR_LIST_LO[ob['status']], conf.STATUS_LIST_LO[ob['status']]]
            #ob['name_type2'] = Templ_locker.objects.get(pk=ob['con_type']).name
            try:
                ob['coup'] = Coupling.objects.get(parrent=ob['id'], parr_type=0)
            except ObjectDoesNotExist:
                ob['coup'] = False
    
    if bu.double:
        d_list = bu.double_list.split(',')
        bu_double = Building.objects.filter(pk__in=d_list)
    
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
    
    v_templ = 'show_build_2.html' if (request.user.groups.filter(name='test').exists()) else 'show_build.html'
    
    return render(request, v_templ,           {'lo_list': locker_list,
                                               'bu': bu,
                                               'kv': kv,
                                               'bu_double': bu_double,
                                               'upr_comp': upr_comp,
                                               'deadline': deadline,
                                               })


####################################################################################################

@login_required(login_url='/core/login/')
def show_locker(request, bu_id, lo_id):

    upd_visit(request.user, 'sh_lo')
    try:
        bu = Building.objects.get(pk=bu_id)
        kv = Kvartal.objects.get(pk=bu.kvar)
        lo = Locker.objects.get(pk=lo_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 2})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
                                               })

    locker_list = Locker.objects.filter(parrent_id=bu_id).order_by('-agr', 'name')\
        .values('id', 'name', 'name_type', 'agr', 'detached', 'co', 'status', 'date_ent', 'rasp', 'prim', 'coord_x', 'coord_y', 'cab_door', 'cab_key', 'object_owner', 'en_model')
    cross_list = Cross.objects.filter(parrent_id=lo_id).order_by('name')\
        .values('id', 'name', 'name_type', 'prim', 'object_owner')
    #device_list = Device.objects.filter(parrent_id=lo_id).values().order_by('name')
    #device_list = Device.objects.filter(parrent_id=lo_id, obj_type__parrent_id__in=[2]).order_by('obj_type__parrent_id').values()
    device_list = Device.objects.filter(parrent_id=lo_id).order_by('obj_type__parrent_id', 'name')\
        .values('id', 'name', 'obj_type__name', 'ip_addr', 'prim', 'object_owner', 'obj_type__parrent_id', 'obj_type__parrent__name')
    boxes_list = Box.objects.filter(parrent_id=lo_id).order_by('name', 'num').values()
    subunit_list = Subunit.objects.filter(parrent_id=lo_id).order_by('name').values()

    if locker_list.count() != 0:
        for ob in locker_list:
            ob['status2'] = [conf.COLOR_LIST_LO[ob['status']], conf.STATUS_LIST_LO[ob['status']]]
            #ob['name_type2'] = Templ_locker.objects.get(pk=ob['con_type']).name
            try:
                ob['coup'] = Coupling.objects.get(parrent=ob['id'], parr_type=0)
            except ObjectDoesNotExist:
                ob['coup'] = False

    if cross_list.count() != 0:
        for cr in cross_list:
            #cr['name_type2'] = Templ_cross.objects.get(pk=cr['con_type']).name
            st_list1 = [0 for i in range(6)]
            st_list2 = [0 for i in range(6)]
            cr_p_list = Cross_ports.objects.filter(parrent_id=cr['id']).order_by('num')
            for cr_p in cr_p_list:
                if not cr_p.p_valid:
                    st_list1[5] += 1
                    st_list2[5] += 1
                else:
                    st_list1[cr_p.up_status] += 1
                    st_list2[cr_p.int_c_status] += 1

            cr['st_list1'] = st_list1
            cr['st_list2'] = st_list2

    if device_list.count() != 0:
        for dev in device_list:
            st_list = [0 for i in range(6)]
            dev_p_list = Device_ports.objects.filter(parrent_id=dev['id']).order_by('num')
            for dev_p in dev_p_list:
                if not dev_p.p_valid:   st_list[5] += 1
                else:                   st_list[dev_p.int_c_status] += 1
            dev['st_list'] = st_list
            #dev['vlan_more'] = False if (len(dev['vlan']) > 20) else True  #длинную строку не показывать    ########
            #pic_type = Templ_device.objects.get(pk=dev['con_type']).parrent_id
            #pic_type = dev['obj_type__parrent_id']
            #dev['pic'] = '/static/images/dev_'+str(dev['obj_type__parrent_id'])+'.png'
            dev['pic'] = f"/static/images/dev_{str(dev['obj_type__parrent_id'])}.png"

    if boxes_list.count() != 0:
        for box in boxes_list:
            #box['name_type2'] = Templ_box.objects.get(pk=box['con_type']).name
            st_list1 = [0 for i in range(6)]
            st_list2 = [0 for i in range(6)]
            box_p_list = Box_ports.objects.filter(parrent_id=box['id']).order_by('num')
            for box_p in box_p_list:
                if not box_p.p_valid:
                    st_list1[5] += 1
                    st_list2[5] += 1
                else:
                    st_list1[box_p.up_status] += 1
                    st_list2[box_p.int_c_status] += 1

            box['st_list1'] = st_list1
            box['st_list2'] = st_list2

    if subunit_list.count() != 0:
        for ob in subunit_list:
            #ob['name_type'] = conf.SUBUNIT_TYPE[ob['con_type']][1]
            name_type = Templ_subunit.objects.get(pk=ob['con_type'])
            subunit_type = Subunit_type.objects.get(pk=name_type.parrent_id)
            ob['name_type'] = [name_type.name, subunit_type.name]
            ob['pic'] = '/static/images/subunit_'+str(subunit_type.id)+'.png'
            ob['poe'] = [conf.POE_TYPE[ob['poe']][1], '/static/images/poe_'+str(ob['poe'])+'.png']
            if ob['box_p_id'] == 0:
                ob['box'] = ''
            else:
                try:
                    ob['box'] = Box_ports.objects.get(pk=ob['box_p_id'],
                                                      parrent__parrent_id=lo_id,
                                                      int_c_status=3,
                                                      dogovor='_su_'+str(ob['id'])
                                                      )
                except ObjectDoesNotExist:
                    ob['box'] = ''
                    su = Subunit.objects.get(pk=ob['id'])
                    su.box_p_id = 0
                    su.save()

    v_templ = 'show_locker_2.html' if (request.user.groups.filter(name='test').exists()) else 'show_locker.html'

    return render(request, v_templ,            {'bu': bu,
                                                'kv': kv,
                                                'lo': lo,
                                                'lo_list': locker_list,
                                                'cr_list': cross_list,
                                                'dev_list': device_list,
                                                'box_list': boxes_list,
                                                'subunit_list': subunit_list,
                                                })


####################################################################################################

@login_required(login_url='/core/login/')
def show_cr(request, bu_id, lo_id, cr_id):
    
    upd_visit(request.user, 'sh_cr')
    try:
        lo = Locker.objects.get(pk=lo_id)
        kv = Kvartal.objects.get(pk=lo.parrent.kvar)
        cr = Cross.objects.get(pk=cr_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})
    try:
        coup = Coupling.objects.get(parrent=lo_id, parr_type=0)
    except ObjectDoesNotExist:
        coup = False

    if lo.parrent_id != int(bu_id) or cr.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/cr='+cr_id+'/'
                                               })

    cr_list = Cross.objects.filter(parrent_id=lo_id).values().order_by('name')
    cr_p_list = Cross_ports.objects.filter(parrent_id=cr.id).values().order_by('num')

    for ob in cr_p_list:
        if ob['up_status'] == 0:            #конечная муфта
            if ob['cab_p_id'] != 0:
                res = chain_trace(ob['id'], '1', transit=True)
                try:
                    if res[0] == 1: c_up = ['', '', 'm: '+res[1].parrent.name, '', '', 'white', '']
                    if res[0] == 2: c_up = ['', '', 'уд: '+res[1].parrent.parrent.name, '', '', 'white', '']
                except:
                    c_up = []
            else:
                c_up = []
            c_up_l = ''
        else:
            try:
                up = Cross_ports.objects.get(pk=ob['up_cross_id'])
                c_up = [up.parrent.parrent.parrent.name,            #0 улица
                        up.parrent.parrent.parrent.house_num,       #1 дом
                        up.parrent.parrent.name,                    #2 УД
                        up.parrent.name,                            #3 кросс
                        str(up.num),                                #4 порт
                        conf.COLOR_CROSS[ob['up_status']],          #5 цвет кроссировки
                        str(up.id)                                  #6 ид противоположного порта для маркера
                        ]
                c_up_l = '../../../build='+str(up.parrent.parrent.parrent.id)+'/locker='+str(up.parrent.parrent.id)+'/cr='+str(up.parrent.id)
            except ObjectDoesNotExist:                              #кроссировка "в пустоту"
                c_up = ['link_err', conf.COLOR_CROSS[ob['up_status']]]
                c_up_l = ''

        if ob['int_c_status'] == 0:
            c_down = []
        else:
            if ob['int_c_dest'] == 1:
                try:
                    down = Cross_ports.objects.get(pk=ob['int_c_id'])
                    c_down = ['кросс',
                              str(down.parrent.name),               #1 имя кросса
                              str(down.num),                        #2 порт
                              conf.COLOR_CROSS[ob['int_c_status']], #3 цвет кроссировки
                              '../cr='+str(down.parrent_id),        #4 ссылка на противоположное оборудование
                              str(down.id)                          #5 ид противоположного порта для маркера
                              ]
                except ObjectDoesNotExist:
                    c_down = ['кросс',
                              'link_err',
                              conf.COLOR_CROSS[ob['int_c_status']]
                              ]
            if ob['int_c_dest'] == 2:
                try:
                    down = Device_ports.objects.get(pk=ob['int_c_id'])
                    c_down = ['акт.обор.',
                              str(down.parrent.name),               #1 имя коммута
                              str(down.num),                        #2 порт
                              conf.COLOR_CROSS[ob['int_c_status']], #3 цвет кроссировки
                              '../dev='+str(down.parrent_id),       #4 ссылка на противоположное оборудование
                              str(down.id)                          #5 ид противоположного порта для маркера
                              ]
                except ObjectDoesNotExist:
                    c_down = ['акт.обор.',
                              'link_err',
                              conf.COLOR_CROSS[ob['int_c_status']]
                              ]

        ob['c_up'] = c_up
        ob['c_up_l'] = c_up_l
        ob['c_down'] = c_down

    try:
        sel = int(request.GET['sel'])
    except:
        sel = False
    try:
        to_print = int(request.GET['to_print'])
    except:
        to_print = False

    return render(request, 'show_cr.html', {'lo': lo,               #текущий шкаф
                                            'kv': kv,               #квартал
                                            'cr_list': cr_list,     #кроссы в текущем шкафу
                                            'cr': cr,               #текущий кросс
                                            'cr_p_list': cr_p_list, #p_list,    #порты текущего кросса
                                            'sel': sel,
                                            'to_print': to_print,
                                            'coup': coup,
                                            })


####################################################################################################

@login_required(login_url='/core/login/')
def show_dev(request, bu_id, lo_id, dev_id, l2=0):
    
    upd_visit(request.user, 'sh_dev')
    try:
        lo = Locker.objects.get(pk=lo_id)
        kv = Kvartal.objects.get(pk=lo.parrent.kvar)
        dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2+int(l2)})

    if lo.parrent_id != int(bu_id) or dev.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3+int(l2)})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1+int(l2),
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/dev='+dev_id+'/'
                                               })

    dev_list = Device.objects.filter(parrent_id=lo_id).order_by('name')
    dev_p_list = Device_ports.objects.filter(parrent_id=dev.id).values().order_by('num')
    dev_p_v_list = Device_ports_v.objects.filter(parrent_id=dev.id).values().order_by('parrent_p', 'vlan_untag')#'p_alias')

    for ob in dev_p_list:
        if ob['int_c_status'] == 0:
            c_down = ['blank.png']
        else:
            if ob['int_c_dest'] == 1:
                try:
                    down = Cross_ports.objects.get(pk=ob['int_c_id'])
                    c_down = ['cr2.png',                            #'кросс ',
                              str(down.parrent.name),               #1 имя кросса
                              str(down.num),                        #2 порт
                              '',                                   #3 N/A
                              '',                                   #4 N/A
                              conf.COLOR_CROSS[ob['int_c_status']], #5 цвет кроссировки
                              'silver',                             #6 N/A
                              '../cr='+str(down.parrent.id),        #7 ссылка на противоположное оборудование
                              '',                                   #8 подменяется, если скроссирован
                              'white',                              #9 нет внешней связи
                              str(down.id)                          #10 ид противоположного порта для маркера
                              ]
                    if down.up_status != 0:
                        c_down[8] = Cross_ports.objects.get(pk=down.up_cross_id)    #8 скроссированный порт кросса
                        c_down[9] = conf.COLOR_CROSS[down.up_status]                #9 цвет кроссировки внешней связи
                except ObjectDoesNotExist:
                    c_down = ['кросс ',
                              'link_err',
                              conf.COLOR_CROSS[ob['int_c_status']]
                              ]

            if ob['int_c_dest'] == 2:
                try:
                    down = Device_ports.objects.get(pk=ob['int_c_id'])
                    #cur_type = Templ_device.objects.get(pk=down.parrent.con_type).parrent_id
                    #cur_type = down.parrent.obj_type.parrent_id
                    c_down = [f"dev_{str(down.parrent.obj_type.parrent_id)}.png",          #'акт.обор. ',
                              str(down.parrent.name),               #1 имя коммута
                              str(down.p_alias),                    #2 порт
                              '',                                   #3 N/A
                              '',   #str(down.num)                  #4 N/A
                              conf.COLOR_CROSS[ob['int_c_status']], #5 цвет кроссировки
                              'silver',                             #6 N/A
                              '../dev='+str(down.parrent.id),       #7 ссылка на противоположное оборудование
                              '',                                   #8 N/A
                              'silver',                             #9 только для внешней связи
                              str(down.id)                          #10 ид противоположного порта для маркера
                              ]
                except ObjectDoesNotExist:
                    c_down = ['акт.обор. ',
                              'link_err',
                              conf.COLOR_CROSS[ob['int_c_status']]
                              ]

            if ob['int_c_dest'] == 3:
                try:
                    down = Box_ports.objects.get(pk=ob['int_c_id'])
                    c_down = ['rj45_2.png',                                 #'КРТ ',
                              str(down.parrent.name+'-'+down.parrent.num),  #1 имя КРТ
                              str(down.p_alias),                            #2 порт КРТ
                              [str(down.dogovor), str(down.ab_kv)],         #3 договор,кв
                              str(down.ab_fio),                             #4 ФИО
                              conf.COLOR_CROSS[ob['int_c_status']],         #5 цвет кроссировки
                              conf.COLOR_CROSS[down.int_c_status],          #6 цвет абонентской кроссировки
                              '../box='+str(down.parrent.id),               #7 ссылка на противоположное оборудование
                              'billing' if down.int_c_status == 1 else '',  #8 статус аб.кроссировки для ссылки в билинг
                              'silver',                                     #9 только для внешней связи
                              str(down.id),                                 #10 ид противоположного порта для маркера
                              ((down.his_ab_kv+'кв') if (down.his_ab_kv != '') else '') + down.his_dogovor  #11 история пары
                              ]
                except ObjectDoesNotExist:
                    c_down = ['КРТ ',
                              'link_err',
                              conf.COLOR_CROSS[ob['int_c_status']]
                              ]

        ob['c_down'] = c_down

        step = 50
        if len(ob['vlan_tag_list']) > step:
            try:
                str1 = ob['vlan_tag_list']
                cnt = 0
                while True:
                    pos = str1.find(',', cnt+step)
                    if pos == -1:
                        break
                    #str1 = str1[:pos+1]+' '+str1[pos+1:]
                    str1 = f"{str1[:pos+1]} {str1[pos+1:]}"
                    cnt = pos + 1
                ob['vlan_tag_list'] = str1
            except:
                ob['vlan_tag_list'] = 'ошибка построения, сообщите разработчику'

    try:
        sel = int(request.GET['sel'])
    except:
        sel = False
    try:
        gog = request.GET['bil_rq']
        bil_rq = from_bgb_gog_rq(gog)
    except:
        bil_rq = [False, False]
    try:
        td = datetime.datetime.now() - dev.date_upd
        tmin,tsec = divmod(td.seconds, 60)
        th, tmin = divmod(tmin, 60)
        #upd_td = [td.days, "%02d"%(th), "%02d"%(tmin), "%02d"%(tsec)]
        upd_td = [td.days, "%02d:%02d:%02d" % (th, tmin, tsec)]
    except:
        upd_td = False

    context = {'lo': lo,
               'kv': kv,
               'dev_list': dev_list,
               'dev': dev,
               'dev_p_list': dev_p_list,#experimental#p_list,
               'sel': sel,
               'bil_rq': bil_rq,
               'upd_td': upd_td,
               'dev_p_v_list': dev_p_v_list,
               }

    templ = 'show_dev_v.html' if (l2 == '1') else 'show_dev.html'

    return render(request, templ, context)


####################################################################################################

@login_required(login_url='/core/login/')
def show_dev_ips(request, bu_id, lo_id, dev_id):

    upd_visit(request.user, 'sh_ips')
    try:
        lo = Locker.objects.get(pk=lo_id)
        kv = Kvartal.objects.get(pk=lo.parrent.kvar)
        dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2+1})

    if lo.parrent_id != int(bu_id) or dev.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3+1})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1+1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/dev='+dev_id+'/'
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
        nonlocal dev_vector
        dev_vector.append(obj[3])
        nonlocal t_list2
        nonlocal t_list3
        if obj[1] == 0:
            t_list2[obj[0]-1][1] = obj
        else:
            obj0 = t_list2[obj[0]-1][0].copy()
            obj0[2] = obj[1]
            t_list3.append([obj0, obj])
###                             проверка на повторяющийся коммут
    def check_vector(dev_id):
        nonlocal dev_vector
        try:
            if dev_id in dev_vector:
                return True
        except:
            pass
        return False
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

    context = {'lo': lo,
               'kv': kv,
               'dev_list': dev_list,
               'dev': dev,
               'total_list2': t_list2,
               }

    return render(request, 'show_dev_ips.html', context)


####################################################################################################

@login_required(login_url='/core/login/')
def show_box(request, bu_id, lo_id, box_id):

    upd_visit(request.user, 'sh_box')
    try:
        lo = Locker.objects.get(pk=lo_id)
        kv = Kvartal.objects.get(pk=lo.parrent.kvar)
        box = Box.objects.get(pk=box_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id) or box.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/box='+box_id+'/'
                                               })
    try:
        select = int(request.GET['sel'])
    except:
        select = 0
    try:
        gog = request.GET['bil_rq']
        bil_rq = from_bgb_gog_rq(gog)
    except:
        bil_rq = [False, False]
    try:
        if bil_rq[0]:
            comm = bil_rq[0]['comment']
            kv = comm.rsplit(' кв ')[1].rsplit(' ')[0]
            box_p = Box_ports.objects.get(pk=select)
            #if box_p.ab_kv == '':
            if box_p.ab_kv != kv:
                h_text = 'УД: '+box.parrent.name+'; крт: '+box.name+'-'+box.num+'-'+box_p.p_alias+'; '
                h_text += 'ab_kv: '+box_p.ab_kv+' -> '+kv+'; '
                box_p.ab_kv = kv
                box_p.save()
                to_his([request.user, 7, box_p.id, 17, 0, h_text])
    except:
        #pass
        to_his([request.user, 4, box.id, 17, 0, 'error- '+str(bil_rq[0]['comment'])])

    box_list = Box.objects.filter(parrent_id=lo_id).values().order_by('name', 'num')
    box_p_list = Box_ports.objects.filter(parrent_id=box.id).values().order_by('num')
    templ_box_cab_list = Templ_box_cable.objects.all()
    i = 1
    cab_count = 1
    for ob in box_p_list:
        if ob['up_status'] == 0:
            c_up = []
            l_up = ''
        else:
            try:
                up = Device_ports.objects.get(pk=ob['up_device_id'])
                c_up = [str(up.parrent.name),
                        str(up.num),
                        str(up.parrent.ip_addr),
                        str(up.id)]
                l_up = '../dev='+str(up.parrent.id)
            except ObjectDoesNotExist:
                c_up = ['link_err']
                l_up = ''

        plint = ob['p_alias'][:1]
        if not plint.isdigit():
            plint = '0'
        ob['c_up'] = c_up
        ob['l_up'] = l_up
        ob['up_color'] = conf.COLOR_CROSS[ob['up_status']]
        ob['int_color'] = conf.COLOR_CROSS[ob['int_c_status']]
        ob['pl_color'] = conf.COLOR_PLINT[int(plint)]
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

    return render(request, 'show_box.html', {'lo': lo,
                                             'kv': kv,
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
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования раздела', 'back': 1})

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
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})
    if lo.parrent_id != int(bu_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 2})
    if lo.agr and not request.user.has_perm("core.can_sh_agr"):
        return render(request, 'denied.html', {'mess': 'нет прав для доступа',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
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
            print(r_dev)
            r_box = box_list.filter(rack_num=ind).exclude(rack_pos=0).values('id', 'name', 'rack_pos', 'con_type')
            cur_rack = []
            #i = 1
            i = ob1[1]
            while i > 0:
                if r_cr.filter(rack_pos=i).count() != 0:
                    cur_cr = r_cr.filter(rack_pos=i).first()
                    cur_units = Templ_cross.objects.get(pk=cur_cr['con_type']).units
                    #ports...
                    cur_rack.append([i, cur_cr, cur_units, 'laser2.png', 'cr='+str(cur_cr['id'])])
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
                    cur_rack.append([i, cur_box, cur_units, 'rj45_2.png', 'box='+str(cur_box['id'])])
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
                cur_rack.append([i, cur_cr, 1, 'laser2.png', 'cr='+str(cur_cr['id'])])
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
    return render(request, 'show_racks.html', {'lo': lo,
                                               'kv': kv,
                                               'form': form,
                                               'rack_list': rack_list,
                                               'adm': request.user.has_perm("kpp.can_adm"),
                                               })
