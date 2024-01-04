# statist__views

import datetime

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
#from django.core.mail import mail_admins
from django.views.decorators.csrf import csrf_exempt

from cross.models import Building
from cross.models import Locker, Device, Box, Subunit
from cross.models import Cross_ports, Device_ports, Box_ports#, Templ_box
from core.models import Templ_device, Templ_subunit
from cable.models import PW_cont, Coupling, Coupling_ports
from core.models import last_visit, Energy_type, Subunit_type, History
from .forms import upl_Form#, stat4_Form#, stat_su_Form#, tb_Form

from core.e_config import conf

from django.http import JsonResponse

#______________________________________________________________________________

@login_required(login_url='/core/login/')
def stat_subunit(request, s_f=0, s_col=0, t_curr=1, xls=0):

    su_list = []
    su_count = 0
    t_choices = Subunit_type.objects.values_list('id', 'name').order_by('id').values_list()#.exclude(id=1)
    #print(t_choices[int(t_curr)-1][1])
    templ = Templ_subunit.objects.filter(parrent_id=int(t_curr)).order_by('parrent_id')
    su_list = Subunit.objects.filter(con_type__in=templ.values_list('id', flat=True))
    sf = ('-' if (str(s_f) == '1') else '')
    if s_col == '1':
        su_list = su_list.order_by(sf+'parrent__name', sf+'name')
    elif s_col == '2':
        su_list = su_list.order_by(sf+'name')
    elif s_col == '3':
        su_list = su_list.order_by(sf+'con_type')
    elif s_col == '4':
        su_list = su_list.order_by(sf+'sn')
    elif s_col == '5':
        su_list = su_list.order_by(sf+'object_owner', sf+'parrent__parrent__name', sf+'parrent__parrent__house_num', sf+'parrent__name')
    elif s_col == '6':
        su_list = su_list.order_by(sf+'date_ent', sf+'parrent__parrent__name', sf+'parrent__parrent__house_num', sf+'parrent__name')
    elif s_col == '7':
        su_list = su_list.order_by(sf+'date_repl', sf+'parrent__parrent__name', sf+'parrent__parrent__house_num', sf+'parrent__name')
    else:
        su_list = su_list.order_by(sf+'parrent__parrent__name', sf+'parrent__parrent__house_num', sf+'parrent__name', sf+'name')
    su_count = su_list.count()

    su_list = su_list.values()
    for ob in su_list:
        ob['addr'] = Locker.objects.get(pk=ob['parrent_id'])
        ob['addr2'] = ob['addr'].parrent.name + ' ' + ob['addr'].parrent.house_num
        ob['addr3'] = ob['addr'].name
        ob['con_type2'] = templ.get(pk=ob['con_type']).name
        ob['date_ent2'] = ob['date_ent'].strftime("%d.%m.%Y") if ob['date_ent'] != None else ''
        ob['date_repl2'] = ob['date_repl'].strftime("%d.%m.%Y") if ob['date_repl'] != None else ''

    if xls:
        name = ['subunit_statistics.xls', t_choices[int(t_curr)-1][1]]
        columns = ('addr2', 'addr3', 'name', 'con_type2', 'sn', 'inv', 'date_ent2', 'date_repl2', 'ip_addr', 'mac_addr', 'object_owner', 'stairway', 'floor', 'prim')
        columns_rus = ('Адрес', 'УД', 'Имя', 'Тип', 'серийный номер', 'инвентарный номер', 'дата ввода', 'дата замены', 'ip-адрес', 'mac-адрес', 'владелец', 'подъезд', 'этаж', 'примечание')
        return import_to_xls(name, su_list, [columns, columns_rus])

    return render(request, 'stat_subunit.html', {
                                'su_list': su_list,
                                'su_count': su_count,
                                'nav': [s_f, s_col, int(t_curr)],
                                't_choices': t_choices,
                                })


def import_to_xls(name, data, col_list):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+ name[0]
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(name[1])
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    for col_num in range(len(col_list[1])):
        ws.write(row_num, col_num, col_list[1][col_num], font_style)
    font_style = xlwt.XFStyle()
    for row in data:#.values_list():
        row_num += 1
        for col_num in range(len(col_list[0])):
            ws.write(row_num, col_num, row[col_list[0][col_num]], font_style)
            #print(row[col_list[0][col_num]])
    wb.save(response)
    return response


#______________________________________________________________________________

def coup_changed(request):

    coup_p = Coupling_ports.objects.filter(changed=True).order_by('id')

    return render(request, 'serv_coup_changed.html', {'p_list': coup_p})


def cable_null_len(request):

    p_list = []
    coup_p = Coupling_ports.objects.filter(fiber_num=1).order_by('id')
    for ob in coup_p:
        info = ob.up_info.split('∿')
        #if ob.up_info.startswith('0,') or ob.up_info == '':
        if info[2] == '0' or info[2] == '':
            p_list.append(ob)

    return render(request, 'serv_cable_null_len.html', {'p_list': p_list, 'count': int(len(p_list)/2)})


####################################################################################################

def dev_no_sn_mac(request):

    #dev_list = Device.objects.filter(Q(ip_addr=None) | Q(sn='') | Q(mac_addr='')).exclude(con_type=3).order_by('name')
    dev_list = Device.objects.filter(Q(ip_addr=None) | Q(sn='') | Q(mac_addr='')).order_by('obj_type', 'name')

    return render(request, 'serv_dev_no_ip_sn_mac.html', {'dev_list':dev_list})


def obj_no_coord(request):

    lo_list = Locker.objects.filter(Q(coord_x__lte=30.0) | Q(coord_y__lte=30.0)).order_by('name')
    coup_list = Coupling.objects.filter(Q(coord_x__lte=30.0) | Q(coord_y__lte=30.0)).order_by('name')
    obj_list = PW_cont.objects.filter(Q(coord_x__lte=30.0) | Q(coord_y__lte=30.0)).order_by('name')

    return render(request, 'serv_obj_no_coord.html', {'lo_list':lo_list,
                                                      'coup_list':coup_list,
                                                      'obj_list':obj_list,
                                                      })


####################################################################################################

def duple_dog(request):

    if not request.user.has_perm("kpp.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    dog_list = []
    box_p_list = list(Box_ports.objects.exclude(int_c_status=0).values_list('dogovor', flat=True))
    for dog in box_p_list:
        if box_p_list.count(dog) != 1:
            dog_list.append(dog)

    return render(request, 'serv_duple_dog.html', {'dog_list':list(set(dog_list))})


####################################################################################################

@login_required(login_url='/core/login/')
def bu_doc(request, bu_id):

    try:
        bu = Building.objects.get(pk=bu_id)
        #kv = Kvartal.objects.get(pk=bu.kvar)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    f_list = []
    #d_exist = True
    f_exist = False

    url = f"doc/{bu.id}/"
    try:
        f_list = default_storage.listdir(url)[1]
        f_list.sort()
    except:
        pass

    if request.method == 'POST':
        if not request.user.has_perm("core.can_adm"):
            return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 0})

        form = upl_Form(request.POST, request.FILES)
        if form.is_valid():
            upl_file = request.FILES['file']
            url_f = url+str(upl_file.name)
            if default_storage.exists(url_f):
                f_exist = True
            else:
                path = default_storage.save(url_f, upl_file)

                return HttpResponseRedirect('/statist/bu_doc='+bu_id)

    form = upl_Form()

    return render(request, 'bu_doc.html', {'bu':bu,
                                           'url':url,
                                           'form':form,
                                           'f_list':f_list,
                                           'f_exist':f_exist,
                                           #'d_exist':d_exist
                                           })


@login_required(login_url='/core/login/')
def bu_doc_del(request, bu_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})

    try:
        bu = Building.objects.get(pk=bu_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    url = 'doc/'+str(bu.id)+'/'

    if request.method == 'POST':
        d_file = request.POST['d_file']
        if default_storage.exists(url+d_file):
            default_storage.delete(url+d_file)
        return HttpResponseRedirect('/statist/bu_doc='+str(bu.id))

    d_file = request.GET['d_file']

    return render(request, 'bu_doc_del.html', {'bu':bu, 'd_file':d_file})


####################################################################################################


@login_required(login_url='/core/login/')
def sync_Coup_lo(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    no_coup_lo = []
    no_lo_coup = []
    locker_list = Locker.objects.all()#.order_by('-agr','name')
    for ob in locker_list:
        if not Coupling.objects.filter(parrent=ob.id, parr_type=0).exists():
            #n_coup = Coupling.objects.create(parrent=ob.id,
            #                                 parr_type=0,
            #                                 name=ob.name+'-Ш',
            #                                 name_type='кассета',
            #                                 )
            #no_coup_lo.append([n_coup.id, n_coup.name])
            no_coup_lo.append([ob.id, ob.name])

    coup_list = Coupling.objects.filter(parr_type=0)#.order_by('name')
    for ob in coup_list:
        if not Locker.objects.filter(pk=ob.parrent).exists():
            no_lo_coup.append([ob.id, ob.name])

    return render(request, 'serv_sync_co_lo.html', {'c1': no_coup_lo, 'c2': no_lo_coup})


####################################################################################################

@login_required(login_url='/core/login/')
def check_link(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    bad_d_b_p, bad_b_d_p, bad_d_d_p, bad_d_c_p, bad_c_d_p, bad_c_c_p = [], [], [], [], [], []
    space_d_b, space_b_d, space_d_d, space_d_c, space_c_d, space_c_c = [], [], [], [], [], []

    d_b_p = Device_ports.objects.filter(int_c_dest=3) #.count()
    b_d_p = Box_ports.objects.exclude(up_device_id=0) #.count()
    d_d_p = Device_ports.objects.filter(int_c_dest=2) #.count()
    d_c_p = Device_ports.objects.filter(int_c_dest=1) #.count()
    c_d_p = Cross_ports.objects.filter(int_c_dest=2)  #.count()
    c_c_p = Cross_ports.objects.filter(int_c_dest=1)  #.count()

    for ob in d_b_p:
        try:
            b_p = Box_ports.objects.get(pk=ob.int_c_id)
            if b_p.up_device_id != ob.id:
                bad_d_b_p.append(str(ob.parrent.name)+' port: '+str(ob.num))
        except ObjectDoesNotExist:
            space_d_b.append(str(ob.parrent.name)+' port: '+str(ob.num))

    for ob in b_d_p:
        try:
            d_p = Device_ports.objects.get(pk=ob.up_device_id)
            if d_p.int_c_id != ob.id:
                bad_b_d_p.append(str(ob.parrent.parrent.name)+' крт: '+str(ob.parrent.name)+'-'+str(ob.parrent.num)+'-'+str(ob.p_alias))
        except ObjectDoesNotExist:
            space_b_d.append(str(ob.parrent.parrent.name)+' крт: '+str(ob.parrent.name)+'-'+str(ob.parrent.num)+'-'+str(ob.p_alias))

    for ob in d_d_p:
        try:
            b_p = Device_ports.objects.get(pk=ob.int_c_id)
            if b_p.int_c_id == ob.id and b_p.int_c_dest == 2:
                pass
            else:
                bad_d_d_p.append(str(ob.parrent.name)+' port: '+str(ob.num))
        except ObjectDoesNotExist:
            space_d_d.append(str(ob.parrent.name)+' port: '+str(ob.num))

    for ob in d_c_p:
        try:
            b_p = Cross_ports.objects.get(pk=ob.int_c_id)
            if b_p.int_c_id == ob.id and b_p.int_c_dest == 2:
                pass
            else:
                bad_d_c_p.append(str(ob.parrent.name)+' port: '+str(ob.num))
        except ObjectDoesNotExist:
            space_d_c.append(str(ob.parrent.name)+' port: '+str(ob.num))

    for ob in c_d_p:
        try:
            b_p = Device_ports.objects.get(pk=ob.int_c_id)
            if b_p.int_c_id == ob.id and b_p.int_c_dest == 1:
                pass
            else:
                bad_c_d_p.append(str(ob.parrent.name)+' port: '+str(ob.num))
        except ObjectDoesNotExist:
            space_c_d.append(str(ob.parrent.parrent.name)+' cr: '+str(ob.parrent.name)+' port: '+str(ob.num))

    for ob in c_c_p:
        try:
            b_p = Cross_ports.objects.get(pk=ob.int_c_id)
            if b_p.int_c_id == ob.id and b_p.int_c_dest == 1:
                pass
            else:
                bad_c_c_p.append(str(ob.parrent.name)+' port: '+str(ob.num))
        except ObjectDoesNotExist:
            space_c_c.append(str(ob.parrent.parrent.name)+' cr: '+str(ob.parrent.name)+' port: '+str(ob.num))

    return render(request, 'serv_check_link.html', {
                                                    'bad_d_b':bad_d_b_p,
                                                    'space_d_b':space_d_b,
                                                    'bad_b_d':bad_b_d_p,
                                                    'space_b_d':space_b_d,
                                                    'bad_d_d':bad_d_d_p,
                                                    'space_d_d':space_d_d,
                                                    'bad_d_c':bad_d_c_p,
                                                    'space_d_c':space_d_c,
                                                    'bad_c_d':bad_c_d_p,
                                                    'space_c_d':space_c_d,
                                                    'bad_c_c':bad_c_c_p,
                                                    'space_c_c':space_c_c,
                                                    })


####################################################################################################

def agr_to_abon(request, dev_id):
    try:
        root_dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})
    #if root_dev.parrent.agr and not request.user.has_perm("kpp.can_sh_agr"):
    #    return render(request, 'denied.html', {'mess': 'нет прав для доступа',
    #                                           'back': 1,
    #                                           #'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/dev='+dev_id+'/'
    #                                           })
###
    def allready_dev(dev_id):
        nonlocal dev_list
        if dev_id in dev_list:
            # print(dev_id)
            return True
        dev_list.append(dev_id)
        return False

    def ch_cr(p_id):
        cr_p = Cross_ports.objects.get(pk=p_id)
        if cr_p.up_status != 0:
            cr_p_up = Cross_ports.objects.get(pk=cr_p.up_cross_id)
            if cr_p_up.int_c_dest == 1:
                ch_cr(cr_p_up.int_c_id)
            elif cr_p_up.int_c_dest == 2:
                ch_dev(cr_p_up.int_c_id)

    def ch_dev(p_id):
        dev_p = Device_ports.objects.get(pk=p_id)
        dev = Device.objects.get(pk=dev_p.parrent_id)
        #dev_type = Templ_device.objects.get(pk=dev.con_type).parrent_id
        #if dev_type in [2, 3, 4]:
        if dev.obj_type.parrent_id in [2, 3, 4]:
            if not allready_dev(dev.id):
                dev_p_list = Device_ports.objects.filter(parrent_id=dev.id).order_by('num').exclude(pk=p_id)
                for port in dev_p_list:
                    ch_port(port)

    def ch_port(port):
        if (port.int_c_dest == 1) and (not port.uplink):
            ch_cr(port.int_c_id)
        elif (port.int_c_dest == 2) and (not port.uplink):
            ch_dev(port.int_c_id)
        elif port.int_c_dest == 3:
            nonlocal box_p_id_list
            box_p_id_list.append(port.int_c_id)
###
###
    dev_list = [root_dev.id]
    root_dev_p_list = Device_ports.objects.filter(parrent_id=root_dev.id).order_by('num')
    if not root_dev_p_list.filter(uplink=True).exists():
        return render(request, 'error.html', {'mess': 'не обозначен ни один аплинк', 'back': 2})

    box_p_id_list = []
    for port in root_dev_p_list:
        ch_port(port)

    box_p_list = Box_ports.objects.filter(pk__in=box_p_id_list).exclude(int_c_status=0).order_by('dogovor')


    return render(request, 'agr_to_abon.html', {'abon_list': box_p_list, 'count': box_p_list.count()})


####################################################################################################

