# find__views

import re

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models import Avg
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from cable.models import PW_cont, Coupling
from cross.models import Kvartal, Building, Locker, Cross, Device, Box, Subunit
from cross.models import Device_ports, Device_ports_v
from core.models import map_slot
#from mess.models import message

from .forms import find_Form_dev, find_Form_agr, find_Form_bu, find_Form_map, find_Form_kv
from app_proc.forms import app_find_Form

from core.shared_def import upd_visit
from core.e_config import conf

####################################################################################################

@login_required(login_url='/core/login/')
def find_0(request, str_id=0):

    return render(request, 'find_start.html', {
                                            'form1': find_Form_bu(initial={'street': str_id}),
                                            'form2': app_find_Form(),
                                            'form3': find_Form_dev(),
                                            'form4': find_Form_agr(),
                                            })

@login_required(login_url='/core/login/')    #(redirect_field_name='my_redirect_field')
def find_bu(request):
    
    upd_visit(request.user, 'f_bu')
    
    if request.method == 'POST':
        form1 = find_Form_bu(request.POST)
        if form1.is_valid():
            street_id = form1.cleaned_data['street']
            h_num = form1.cleaned_data['house_num']
            bu = Building.objects.filter(parrent_id=street_id).order_by('house_num')
            #context = {'str_list': bu, 'str_id': street_id}
            context = {
                        'str_list': ch_bu_lo(bu.values()),
                        'form1': find_Form_bu(initial={'street': street_id}),
                        'form2': app_find_Form(),
                        'form3': find_Form_dev(),
                        'form4': find_Form_agr(),
                        }
            if (bu.count()) == 0:
                return HttpResponseRedirect('/find/str='+str(street_id))
            if h_num != '':
                bu2 = bu.filter(house_num=h_num)
                if (bu2.count()) == 1:
                    bu_id = bu2.values('id')[0]['id']
                    return HttpResponseRedirect('/cross/build='+str(bu_id))    
                
            return render(request, 'find_result.html', context)

    return HttpResponseRedirect('/find')


def ch_bu_lo(bu):
    
    for ob in bu:
        lo = Locker.objects.filter(parrent_id=int(ob['id'])).values('status', 'agr', 'detached').order_by('-agr', 'name')
        ob['lo'] = []
        for ob2 in lo:
            ob['lo'].append(
                            [conf.COLOR_LIST_LO[ob2['status']],
                            #conf.STATUS_LIST_LO[ob2['status']],
                            ob2['agr'],
                            ob2['detached']
                            ])

    return bu


####################################################################################################

@login_required(login_url='/core/login/')
def find_agr(request):

    upd_visit(request.user, 'f_agr')
    if request.method == 'POST':
        form4 = find_Form_agr(request.POST)
        if form4.is_valid():
            a_co = form4.cleaned_data['co']
            if a_co == 'all':
                agr = Locker.objects.filter(agr=True).order_by('co')#.values()
                return render(request, 'find_result.html', {
                                                            'agr': agr,
                                                            'form1': find_Form_bu(),
                                                            'form2': app_find_Form(),
                                                            'form3': find_Form_dev(),
                                                            'form4': find_Form_agr,
                                                            })
            else:
                try:
                    agr = Locker.objects.get(agr=True, co=a_co)
                    return HttpResponseRedirect('/cross/build='+str(agr.parrent_id)+'/locker='+str(agr.id))
                except ObjectDoesNotExist:
                    return HttpResponseRedirect('/find')
                
    return HttpResponseRedirect('/find')


####################################################################################################

@login_required(login_url='/core/login/')
def find_dev(request, param_id):

    upd_visit(request.user, 'f_dev')

    ok = False
    txt = ''
    dev_list = []
    dev_list_f = []
    dev_list_v = []
    dev_list_tag = []
    su_list = []
    if request.method == 'POST':# and param_id != '0':
        form3 = find_Form_dev(request.POST)
        if param_id == '1':
            txt = form3.data['dev_ip'].strip()
            if re.match(conf.IP_RE, txt):
                ip = txt.replace(',', '.')
                dev_list = Device.objects.filter(ip_addr=ip)
                dev_list_f = Device_ports.objects.filter(ip__startswith=ip)
                dev_list_v = Device_ports_v.objects.filter(ip__startswith=ip)
                su_list = Subunit.objects.filter(ip_addr=ip)
                ok = True
        if param_id == '2':
            txt = form3.data['dev_mac'].strip()
            if re.match(conf.MAC_RE, txt) and len(txt) == 17:
                mac = txt.replace('-', ':').upper()
                dev_list = Device.objects.filter(mac_addr=mac)
                su_list = Subunit.objects.filter(mac_addr=mac)
                ok = True
        if param_id == '3':
            txt = form3.data['dev_sn'].strip()
            if txt != '':
                dev_list = Device.objects.filter(sn=txt)
                su_list = Subunit.objects.filter(Q(sn=txt) | Q(inv=txt))
                ok = True
        if param_id == '4':
            txt = form3.data['dev_vlan'].strip()
            if (len(txt) < 5) and txt.isdigit():
                ok = True
                #dev_list_f = Device_ports.objects.filter(vlan_untag=txt.replace(' ', ''))
                dev_f = Device_ports.objects.exclude(vlan_untag='')
                dev_list_f = find_vlan(dev_f, 'ob.vlan_untag', txt)
                #dev_list_v = Device_ports_v.objects.filter(vlan_untag=txt.replace(' ', ''))
                dev_v = Device_ports_v.objects.exclude(vlan_untag='')
                dev_list_v = find_vlan(dev_v, 'ob.vlan_untag', txt)
                dev = Device_ports.objects.exclude(vlan_tag_list='')
                dev_list_tag = find_vlan(dev, 'ob.vlan_tag_list', txt)
        
        return render(request, 'find_result.html', {
                                                    'txt': txt,
                                                    'param': conf.DEV_FIND_PARAM[int(param_id)-1],
                                                    'dev_list': dev_list,
                                                    'dev_list_f': dev_list_f,
                                                    'dev_list_v': dev_list_v,
                                                    'dev_list_tag': dev_list_tag,
                                                    'su_list': su_list,
                                                    'form1': find_Form_bu(),
                                                    'form2': app_find_Form(),
                                                    'form3': form3,
                                                    'form4': find_Form_agr,
                                                    'ok_dev': ok,
                                                    })
    return HttpResponseRedirect('/find')


def find_vlan(qs_ports, type_p, txt):

    list_ports = []
    for ob in qs_ports:
        if eval(type_p) == txt:
            list_ports.append(ob)
        else:
            vl_l = eval(type_p).split(',')
            for ob2 in vl_l:
                if ob2 == txt:
                    list_ports.append(ob)
                    break
                else:
                    ob3 = ob2.split('-')
                    if len(ob3) == 2:
                        if int(txt) >= int(ob3[0]) and int(txt) <= int(ob3[1]):
                            list_ports.append(ob)
                            break

    return list_ports


####################################################################################################
####################################################################################################

@login_required(login_url='/core/login/')
def maps(request, m_num=1):

    upd_visit(request.user, 'map'+str(m_num))

    form_init1 = {}
    form_init2 = {}
    try:
        crd = request.GET['coord'].split(',')
        c_x = crd[0]
        c_y = crd[1]
        lo = Locker.objects.filter(coord_x=float(c_x), coord_y=float(c_y))
        if lo.count() != 0:
            form_init1 = {'street': lo.first().parrent.parrent_id}
            form_init2 = {'kvar': lo.first().parrent.kvar}
        #не будет работать, пока поле locker.co не индекс
        #    if lo.first().agr == True:
        #        form_init1.update({'agr_list': str(lo.first().co)})
    except:
        c_x = False
        c_y = False

    form1 = find_Form_map(initial=form_init1)
    form2 = find_Form_kv(initial=form_init2)
    
    map_list = map_slot.objects.all().order_by('num').values_list()
    #print(map_list)
    #print(m_num)
    if int(m_num) == 1:
        map_perm = True
    else:
        map_perm = True if (request.user.groups.filter(name='map_' + str(m_num) + '_view').exists()) else False
    
    return render(request, 'maps.html', {
                                            'form1': form1,
                                            'form2': form2,
                                            'c_x': c_x,
                                            'c_y': c_y,
                                            'map': True,           #для заголовка вкладки
                                            'm_num': int(m_num),   #номер слота карты
                                            'map_list': map_list,  #список слотов карт
                                            'map_perm': map_perm,  #права на просмотр карты
                                            #'agr_list': agr_list,
                                            })


####################################################################################################

#@csrf_exempt
def get_obj(request):

    lo_list, co_list, pw_list = [], [], []
    blur = 25       #квадрат для охвата координат
    #offset = -0     #смещение вправо, вниз
    try:
        coord = request.GET['coord'].split(',')
        c_x = float(coord[0])
        c_y = float(coord[1])
        lo_list = Locker.objects.filter(coord_x__range=(c_x-blur, c_x+blur), coord_y__range=(c_y-blur, c_y+blur)).order_by('-agr', 'name')
        co_list = Coupling.objects.filter(coord_x__range=(c_x-blur, c_x+blur), coord_y__range=(c_y-blur, c_y+blur)).order_by('name')
        pw_list = PW_cont.objects.filter(coord_x__range=(c_x-blur, c_x+blur), coord_y__range=(c_y-blur, c_y+blur)).order_by('name')
    except:
        pass
        #print('1')
    try:
        bu_id = int(request.GET['bu'])
        bu = Building.objects.get(pk=bu_id)
        lo_list = Locker.objects.filter(parrent_id=bu_id).order_by('-agr', 'name')
        #co_list = Coupling.objects.filter().order_by('name')
        #pw_list = PW_cont.objects.filter().order_by('name')
    except:
        pass
        #print('2')
    try:
        lo_id = int(request.GET['agr'])
        lo = Locker.objects.get(pk=lo_id)
        lo_list.append(lo)
        co_list = Coupling.objects.filter(parr_type=0, parrent=lo.id).order_by('name')
        #pw_list = PW_cont.objects.filter().order_by('name')
    except:
        pass
        #print('3')

    return render(request, 'get_obj.html', {
                                            'lo_list': lo_list,
                                            'co_list': co_list,
                                            'pw_list': pw_list,
                                            })


####################################################################################################

#@csrf_exempt
def js_request(request):

    try:
        sel_str_id = request.GET['str']
        sel_bu = Building.objects.filter(parrent_id=sel_str_id).values_list('house_num').order_by('house_num')
        return HttpResponse(sel_bu)
    except:
        pass

    try:
        str_bu = request.GET['bu']
        get = str_bu.split(',,')
        if len(get[1]) == 0:
            return HttpResponse(False)
        bu = Building.objects.get(parrent_id=int(get[0]), house_num=str(get[1]))
        lo_list = Locker.objects.filter(parrent_id=bu.id)
        bu_x = int(lo_list.aggregate(average_x=Avg('coord_x'))['average_x']) if lo_list.count() != 0 else 0
        bu_y = int(lo_list.aggregate(average_y=Avg('coord_y'))['average_y']) if lo_list.count() != 0 else 0
        #print(get)
        return HttpResponse(str(bu_x)+','+str(bu_y)+','+str(bu.id))
    except:
        pass

    try:
        co = request.GET['agr']
        if co == '---':
            return HttpResponse(False)
        agr = Locker.objects.get(agr=True, co=co)
        co_x = agr.coord_x
        co_y = agr.coord_y

        return HttpResponse(str(co_x)+','+str(co_y)+','+str(agr.id)+','+str(agr.parrent_id))
    except:
        pass

    try:
        kv_id = request.GET['kv']
        #print(kv_id)
        bu_list = Building.objects.filter(kvar=kv_id).values_list('id', flat=True)
        lo_list = Locker.objects.filter(parrent__kvar=kv_id).values_list('id', flat=True)
        coup_list = Coupling.objects.filter(Q(parr_type=0, parrent__in=lo_list) | Q(parr_type=1, parrent__in=bu_list))
        pw_list = PW_cont.objects.filter(parrent_id=kv_id)
        #print(pw_list)
        c_x = int(coup_list.aggregate(average_x=Avg('coord_x'))['average_x']) if coup_list.count() != 0 else 0
        c_y = int(coup_list.aggregate(average_y=Avg('coord_y'))['average_y']) if coup_list.count() != 0 else 0
        p_x = int(pw_list.aggregate(average_x=Avg('coord_x'))['average_x']) if pw_list.count() != 0 else 0
        p_y = int(pw_list.aggregate(average_y=Avg('coord_y'))['average_y']) if pw_list.count() != 0 else 0
        #print(c_x, c_y, p_x, p_y)
        crd_x = int((c_x+p_x)/2) if (c_x != 0 and p_x != 0) else c_x+p_x
        crd_y = int((c_y+p_y)/2) if (c_y != 0 and p_y != 0) else c_y+p_y

        return HttpResponse(str(crd_x)+','+str(crd_y)+','+str(kv_id))
    except:
        pass

    return HttpResponse(False)


####################################################################################################
"""
#@csrf_exempt
def js_request_mess(request):

    try:
        user_id = request.GET['uid']
        if (int(user_id) != request.user.id):
            return HttpResponse(False)
        user_grp = request.user.groups.all().values_list('id', flat=True)
        m_cnt_u = message.objects.filter(date_2=None).filter(gr_list__in=user_grp).count()
        m_cnt_all = message.objects.filter(date_2=None).filter(gr_list=0).count()

        return HttpResponse(str(m_cnt_u)+'/'+str(m_cnt_all))
    except:
        pass

    return HttpResponse(False)
"""

