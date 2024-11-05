# statist__views

import datetime

from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

from cross.models import Building
from cross.models import Locker, Device, Box, Subunit
from cross.models import Cross_ports, Device_ports, Box_ports
from core.models import Templ_device, Templ_subunit
from cable.models import PW_cont, Coupling, Coupling_ports
from core.models import last_visit, Energy_type, Subunit_type, History
from .forms import upl_Form, stat4_Form

from core.e_config import conf


def get_ip_list(request, con_type):
    dev_list = []  # Device.objects.filter(con_type=con_type).exclude(ip_addr=None).values_list('ip_addr', flat=True)
    ###
    # dev_list = dev_list.filter(parrent__co='CO-1')
    # dev_list = dev_list.filter(ip_addr__in=['192.168.1.111','192.168.1.113'])
    ###
    return JsonResponse({'ip_list': list(dev_list)})


def stat(request):
    start_date_30 = datetime.date.today() - datetime.timedelta(30)
    start_date_60 = datetime.date.today() - datetime.timedelta(60)
    end_date = datetime.date.today()

    dev = Templ_device.objects.all().order_by('parrent_id', 'id').values()
    for ob in dev:
        ob['dev'] = Device.objects.filter(obj_type_id=ob['id']).count()

    lo = (Locker.objects.all().count(),                                                         # 0
          Locker.objects.filter(status=0).count(),                                              # 1
          Locker.objects.filter(status=1).count(),                                              # 2
          Locker.objects.filter(status=2).exclude(co='---').exclude(agr=True).count(),          # 3
          Locker.objects.filter(status=2, date_ent__range=(start_date_60, end_date)).count(),   # 4
          Locker.objects.filter(detached=True).exclude(co='---').exclude(agr=True).count(),     # 5
          Locker.objects.filter(co='---').count(),                                              # 6
          Locker.objects.filter(status=3).count()                                               # 7
          )
    coup = (None, # Coupling.objects.filter(parr_type=0).count(),                               # 0
            Coupling.objects.filter(parr_type=1).count(),                               # 1
            Coupling.objects.filter(parr_type=2).count(),                               # 2
            Coupling_ports.objects.filter(int_c_id=0).count(),                          # 3
            int(Coupling_ports.objects.filter(int_c_dest=0).count() / 2),               # 4
            Coupling_ports.objects.filter(int_c_dest=1).count(),                        # 5
            Coupling_ports.objects.filter(changed=True).count()                         # 6
            )
    box = (Box.objects.exclude(con_type=3).count(),  # 0
           Box_ports.objects.filter(int_c_status=0, p_valid=True).exclude(parrent__con_type=3).count(),                 # 1
           Box_ports.objects.filter(int_c_status=1, p_valid=True).exclude(parrent__con_type=3).count(),                 # 2
           Box_ports.objects.filter(int_c_status=3, p_valid=True).exclude(parrent__con_type=3).count(),                 # 3
           0,                                                                                                           # 4
           Box_ports.objects.filter(p_valid=False).exclude(parrent__name_type='крт напрямую').count(),                  # 5
           Box_ports.objects.filter(int_c_status=2, p_valid=True, parrent__parrent__co__in=conf.OFFICE_LIST[1]).count(),# 6
           Box_ports.objects.filter(int_c_status=2, p_valid=True, parrent__parrent__co__in=conf.OFFICE_LIST[1], date_cr__lt=start_date_30).count(),  # 7
           Box_ports.objects.filter(int_c_status=2, p_valid=True, parrent__parrent__co__in=conf.OFFICE_LIST[2]).count(),# 8
           Box_ports.objects.filter(int_c_status=2, p_valid=True, parrent__parrent__co__in=conf.OFFICE_LIST[2], date_cr__lt=start_date_30).count(),  # 9
           Box_ports.objects.filter(changed=True).exclude(parrent__name_type='крт напрямую').count(),                   # 10
           )

    return render(request, 'stat.html', {'lo': lo, 'dev': dev, 'coup': coup, 'box': box, 'title': 'сервис | отчеты'})


@login_required(login_url='/core/login/')
def stat2(request):

    st_list = []
    bu = Building.objects.all().order_by('name', 'house_num')
    lo_c, dev_c, p1_c, box_c = 0, 0, 0, 0

    for ob in bu:
        lo = Locker.objects.filter(parrent=ob.id).exclude(co='---').exclude(agr=True)\
                            .exclude(detached=True).order_by('id')
        dev = Device.objects.filter(parrent__parrent=ob.id).exclude(parrent__co='---')\
                            .exclude(parrent__agr=True).exclude(parrent__detached=True)#.filter(obj_type_id__in=(1, 2))
        if dev.count() == 0:
            #st_list.append(['0'])
            continue
        port_1 = Device_ports.objects.filter(parrent__in=dev)
        port_2 = port_1.filter(int_c_dest=3)
        box_p = 0
        for ob2 in port_2:
            bp = Box_ports.objects.get(pk=ob2.int_c_id)
            if bp.int_c_status != 0:
                box_p += 1
        st_list.append([ob,
                        lo.count(),
                        dev.count(),
                        port_1.count(),
                        port_2.count(),
                        box_p,
                        ])
        lo_c += lo.count()
        dev_c += dev.count()
        p1_c += port_1.count()
        box_c += box_p

    return render(request, 'stat2.html', {'st_list': st_list,
                                          'c_list': [lo_c, dev_c, p1_c, box_c],
                                          })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def stat3(request):

    lo_list = []
    lo = Locker.objects.exclude(co='---').exclude(agr=True).exclude(detached=True).order_by('parrent__name')

    for ob in lo:
        dev = Device.objects.filter(parrent=ob.id, obj_type_id__in=[1, 2])
        if dev.count() == 0:
            continue
        dev_p = Device_ports.objects.filter(parrent__in=dev)
        dev_p_box = dev_p.filter(int_c_dest=3)
        dev_p_act = 0
        for ob2 in dev_p_box:
            bp = Box_ports.objects.get(pk=ob2.int_c_id)
            if bp.int_c_status != 0:
                dev_p_act += 1

        lo_list.append([ob,
                        dev.count(),
                        dev_p.count(),
                        dev_p_box.count(),
                        dev_p_act,
                        int(round(dev_p_act / dev_p.count() * 100, 0))
                        ])

    return render(request, 'stat3.html', {'lo_list': lo_list})


#______________________________________________________________________________

@login_required(login_url='/core/login/')
def stat4(request):
    #if not request.user.has_perm("core.can_adm"):
    #    return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 0})

    val_list = ['id', 'up_device_id', 'parrent_id', 'parrent__parrent_id', 'parrent__parrent__parrent_id',
                'dogovor', 'parrent__parrent__co', 'parrent__parrent__parrent__name',
                'parrent__parrent__name', 'parrent__parrent__parrent__house_num']

    if request.method == 'POST':
        form = stat4_Form(request.POST)
        dog_filter = request.POST['dog_filter']
        if dog_filter == 'all':
            box_list = Box_ports.objects.exclude(dogovor='').values(*val_list)
        else:
            box_list = Box_ports.objects.filter(dogovor__startswith=dog_filter).values(*val_list)\
                .order_by('parrent__parrent__co', 'parrent__parrent__parrent__name', 'parrent__parrent__parrent__house_num')
    else:
        form = stat4_Form()
        box_list = []

    for b_p in box_list:
        try:
            d_p = Device_ports.objects.get(pk=b_p['up_device_id'])
            b_p['commut'] = (d_p.parrent.obj_type.name, d_p.parrent.ip_addr, d_p.num, d_p.p_alias)
            # print(b_p['commut'])
        except ObjectDoesNotExist:
            pass

    return render(request, 'stat4.html', {'form': form, 'box_list': box_list})


#______________________________________________________________________________
@login_required(login_url='/core/login/')
def stat_energy(request):

    if not request.user.has_perm("core.can_edit_en"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    lo_list = Locker.objects.filter(en_model__gte=2).exclude(co='---') #.values()#.order_by('id')
    en_list = []
    for ob in lo_list:
        en_list.append([ob.parrent.name,
                        ob.parrent.house_num,
                        ob.parrent_id,
                        ob.id,
                        ob.name,
                        Energy_type.objects.get(pk=ob.en_model).name,
                        ob.en_sn,
                        ob.en_date_reg,
                        ob.en_date_check,
                        ob.en_meter.split(','),
                        ])

    return render(request, 'stat_energy.html', {'lo_list': en_list})


#______________________________________________________________________________

@login_required(login_url='/core/login/')
@csrf_exempt
def stat_bu(request):

    lo_st = []
    lo_c = 0
    bu_c = 0
    lo_nodate = 0
    if request.method == 'POST':
        try:
            start_date = datetime.datetime.strptime(request.POST['start_date'], '%d.%m.%Y').date()
        except:
            start_date = datetime.datetime.strptime('01.01.2009', '%d.%m.%Y').date()
        try:
            end_date = datetime.datetime.strptime(request.POST['end_date'], '%d.%m.%Y').date()
        except:
            end_date = datetime.date.today()
        
        lo_st = Locker.objects.filter(date_ent__range=(start_date, end_date)).order_by('date_ent')#.values_list('pk', flat=True)
        lo_c = lo_st.count()
        #lo_st = Locker.objects.filter(date_ent__range=(start_date, end_date)).order_by('date_ent').values_list('pk', flat=True)
        bu_st = Building.objects.filter(pk__in=list(lo_st.values_list('parrent', flat=True)))
        bu_c = bu_st.count()
        lo_nodate = Locker.objects.filter(status=2, date_ent=None).count()
        
    else:
        start_date = datetime.datetime.strptime('01.01.2009', '%d.%m.%Y').date()
        end_date = datetime.date.today()

    return render(request, 'stat_bu.html', {'lo_st': lo_st,
                                            'lo_c': lo_c,
                                            'bu_c': bu_c,
                                            'lo_nodate': lo_nodate,
                                            'start_date': start_date,
                                            'end_date': end_date
                                            })


@login_required(login_url='/core/login/')
def stat_lo(request):

    start_date = datetime.date.today() - datetime.timedelta(60)
    end_date = datetime.date.today()

    lo_st0 = Locker.objects.filter(status=0).order_by('date_ent')
    lo_st1 = Locker.objects.filter(status=1).order_by('date_ent')
    lo_st2 = Locker.objects.filter(status=2, date_ent__range=(start_date, end_date)).order_by('date_ent')
    lo_st3 = Locker.objects.filter(status=3).order_by('date_ent')

    return render(request, 'stat_lo.html', {'st0':lo_st0, 'st1':lo_st1, 'st2':lo_st2, 'st3':lo_st3})


@login_required(login_url='/core/login/')
def stat_lo_det(request):

    lo_det = Locker.objects.filter(detached=True).exclude(co='---').exclude(agr=True).order_by('date_ent')

    return render(request, 'stat_lo.html', {'lo_det': lo_det})


@login_required(login_url='/core/login/')
def stat_lo_noco(request):

    lo_noco = Locker.objects.filter(co='---').order_by('name')

    return render(request, 'stat_lo.html', {'lo_noco': lo_noco})


def stat_dev_type(request, t_id):

    dev_list = Device.objects.filter(obj_type_id=t_id).order_by('parrent__co', 'name')

    return render(request, 'stat_dev_type.html', {'dev_list': dev_list, 'type': dev_list.first().obj_type.name})


def stat_dev_br(request):

    dev_p = Device_ports.objects.filter(int_c_status=2).order_by('id')
    pag = Paginator(dev_p, 34)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)

    return render(request, 'stat_dev.html', {'p_list': p_list, 'br': True})


def stat_dev_bad(request):

    dev_p = Device_ports.objects.filter(p_valid=False).order_by('id')
    pag = Paginator(dev_p, 34)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)

    return render(request, 'stat_dev.html', {'p_list': p_list, 'bad': True})


def stat_dev_all(request):

    dev_list = Device.objects.all().order_by('parrent__co', 'obj_type__parrent_id', 'name')\
        .values('parrent__co', 'parrent__parrent__name', 'parrent__parrent__house_num', 'parrent__name',
                'parrent__status', 'parrent__parrent__id', 'parrent__id', 'obj_type__parrent__name', 'obj_type__name',
                'id', 'name', 'sn', 'ip_addr', 'mac_addr', 'ip_mask', 'ip_gateway', 'vlan', 'vers_po',
                'man_conf', 'man_install', 'date_ent', 'date_repl', 'date_upd', 'prim', 'object_owner')

    name = ['device_statistics.xls', 'all devices']
    columns = ('parrent__co', 'parrent__parrent__name', 'parrent__parrent__house_num', 'parrent__name', 'name',
               'obj_type__parrent__name', 'obj_type__name', 'sn', 'mac_addr', 'ip_addr', 'ip_mask', 'ip_gateway',
               'vlan', 'vers_po', 'man_conf', 'man_install', 'date_ent', 'date_repl', 'date_upd', 'object_owner', 'prim')
    columns_rus = ('CO', 'улица', '№ здания', 'УД', 'название', 'тип', 'модель', 'sn', 'mac', 'ip', 'mask', 'gateway',
                   'vlan', 'версия по', 'подготовил', 'установил', 'дата ввода',
                   'дата замены', 'дата последнего обн.конфига', 'владелец', 'примечание')
    return import_to_xls(name, dev_list, [columns, columns_rus])
    #return render(request, 'stat_dev_all.html', {'dev_list': dev_list})


def stat_box_br(request, co):

    start_date = datetime.date.today() - datetime.timedelta(30)

    if co == '1' or co == '2':
        dev_p = Box_ports.objects.filter(int_c_status=2).filter(parrent__parrent__co__in=conf.OFFICE_LIST[int(co)]).order_by('date_cr')
    else:
        dev_p = Box_ports.objects.filter(int_c_status=2).filter(parrent__parrent__co__in=conf.OFFICE_LIST[0]).order_by('date_cr')

    pag = Paginator(dev_p, 34)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)

    return render(request, 'stat_box.html', {'p_list': p_list, 'date_exp': start_date, 'br': True})


def stat_box_bad(request):

    dev_p = Box_ports.objects.filter(p_valid=False).order_by('id')
    pag = Paginator(dev_p, 34)
    page = request.GET.get('page')
    try:
        p_list = pag.page(page)
    except PageNotAnInteger:
        p_list = pag.page(1)
    except EmptyPage:
        p_list = pag.page(pag.num_pages)

    return render(request, 'stat_box.html', {'p_list': p_list, 'bad': True})


def stat_box_uninstall(request):

    dev_p = Box_ports.objects.filter(changed=True).order_by('id')

    return render(request, 'stat_box.html', {'p_list': dev_p, 'uninstall': True})

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

# def dev_no_sn_mac(request):
#     dev_list = Device.objects.filter(Q(ip_addr=None) | Q(sn='') | Q(mac_addr='')).order_by('obj_type', 'name')
#
#     return render(request, '-serv_dev_no_ip_sn_mac.html', {'dev_list':dev_list})


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

    if not request.user.has_perm("core.can_adm"):
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
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    f_list = []
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
            url_f = f'{url}{upl_file.name}'
            if default_storage.exists(url_f):
                f_exist = True
            else:
                path = default_storage.save(url_f, upl_file)

                return HttpResponseRedirect(f'/statist/bu_doc={bu_id}/')

    form = upl_Form()

    return render(request, 'bu_doc.html', {'bu': bu,
                                           'url': url,
                                           'form': form,
                                           'f_list': f_list,
                                           'f_exist': f_exist
                                           })


@login_required(login_url='/core/login/')
def bu_doc_del(request, bu_id):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 1})

    try:
        bu = Building.objects.get(pk=bu_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    url = f'doc/{bu.id}/'

    if request.method == 'POST':
        d_file = request.POST['d_file']
        if default_storage.exists(url+d_file):
            default_storage.delete(url+d_file)
        return HttpResponseRedirect(f'/statist/bu_doc={bu.id}/')

    d_file = request.GET['d_file']

    return render(request, 'bu_doc_del.html', {'bu': bu, 'd_file': d_file})

####################################################################################################


@login_required(login_url='/core/login/')
def sync_Coup_lo(request):

    if not request.user.has_perm("core.can_adm"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    no_coup_lo, no_lo_coup = [], []
    locker_list = Locker.objects.all()
    for ob in locker_list:
        if not Coupling.objects.filter(parrent=ob.id, parr_type=0).exists():
            no_coup_lo.append([ob.id, ob.name])

    coup_list = Coupling.objects.filter(parr_type=0)
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
                                                    'bad_d_b': bad_d_b_p,
                                                    'space_d_b': space_d_b,
                                                    'bad_b_d': bad_b_d_p,
                                                    'space_b_d': space_b_d,
                                                    'bad_d_d': bad_d_d_p,
                                                    'space_d_d': space_d_d,
                                                    'bad_d_c': bad_d_c_p,
                                                    'space_d_c': space_d_c,
                                                    'bad_c_d': bad_c_d_p,
                                                    'space_c_d': space_c_d,
                                                    'bad_c_c': bad_c_c_p,
                                                    'space_c_c': space_c_c,
                                                    })


@login_required(login_url='/core/login/')
def stat_block_ports(request):

    if not request.user.has_perm("core.can_telnet"):
        return render(request, 'denied.html', {'mess': 'insufficient access rights', 'back': 2})

    now = datetime.datetime.now()
    bu_list = Building.objects.filter(double_id=0).order_by('name', 'house_num')
    st_list = []
    for bu in bu_list:
        #lo_c = Locker.objects.filter(parrent=bu.id).exclude(co='---').exclude(agr=True).order_by('id').count()
        lo_c = Locker.objects.filter(parrent=bu.id).exclude(status=3).count()
        #dev_c = Device.objects.filter(parrent__parrent=bu.id).exclude(parrent__co='---').exclude(parrent__agr=True).filter(con_type__in=[1, 2]).count()
        dev_c = Device.objects.filter(parrent__parrent=bu.id).exclude(parrent__status=3).filter(obj_type_id__in=[1, 2]).count()
        his = History.objects.filter(obj_type=0, obj_id=bu.id, operation1=18).last()
        if his:
            d_days = (now - his.time_rec).days
            if d_days < 10:     color = 'green'
            elif d_days < 30:   color = 'yellow'
            else:               color = 'orange'
            st_list.append([bu, lo_c, dev_c, his.time_rec, d_days, color])
        else:
            color = 'red' if dev_c != 0 else 'white'
            st_list.append([bu, lo_c, dev_c, False, False, color])

    return render(request, 'stat_block_ports.html', {'st_list': st_list, 'bu_count': bu_list.count()})


####################################################################################################

@login_required(login_url='/core/login/')
def agr_to_abon(request, dev_id):
    try:
        root_dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

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
        if dev.obj_type.parrent_id in (2, 3, 4):
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


@login_required(login_url='/core/login/')
def suspicious_ip(request):

    dev_list = []
    dev_l = Device.objects.exclude(ip_addr=None)
    for dev in dev_l:
        o1, o2, o3, _ = dev.ip_addr.split('.')
        if len(o1) != 3 or len(o2) != 3:
            if o1 == '10' and o2 == '0' and o3 in ('3', '5'):
                continue
            if o1 == '172' and o2 == '18' and o3 == '255':
                continue
            if o1 == '172' and o2 == '21':
                continue
            dev_list.append(dev)

    return render(request, 'suspicious_ip.html', {'dev_list': dev_list})

####################################################################################################


@login_required(login_url='/core/login/')
def stat_last_update_config(request):

    now = datetime.datetime.now()
    dev_list = Device.objects.exclude(ip_addr=None)\
        .values('parrent__parrent__id', 'parrent__id', 'id', 'name', 'obj_type__name', 'ip_addr', 'date_upd')\
        .order_by('date_upd')

    for dev in dev_list:
        if dev['date_upd']:
            d_days = (now - dev['date_upd']).days
            if d_days < 3:      color = 'green'
            elif d_days < 14:   color = 'yellow'
            else:               color = 'orange'
        else:
            d_days = False
            color = 'red'

        dev['d_days'] = d_days
        dev['color'] = color

    return render(request, 'stat_last_update_config.html', {'dev_list': dev_list})

####################################################################################################


@login_required(login_url='/core/login/')
def stat_log_update_config(request):

    log_list = []
    report_file = "report/upd_config_log.txt"
    rep_list = default_storage.open(report_file, mode='rb')

    for ob in rep_list:
        #temp = ob.strip().split('|')
        #log_list.append(list(map(lambda st: st.strip(), temp)))
        log_list.append(ob.decode("utf-8").strip()) #.encode("utf-8")

    log_list.reverse()

    try:
        _ = request.GET['get_file']
        response = HttpResponse(content_type='application/text;')
        response['Content-Disposition'] = 'inline; filename='+report_file
        response['Content-Transfer-Encoding'] = 'binary'
        response.write('\n'.join(log_list))

        return response

    except Exception as error:
        pass #return render(request, 'error.html', {'mess': str(error), 'back': 1})

    return render(request, 'stat_log_update_config.html', {'log_list': log_list})

