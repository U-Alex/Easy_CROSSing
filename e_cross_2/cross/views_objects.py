# cross__views_objects

import datetime
import re

from django.contrib.auth.decorators import login_required
#from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
#from django.db.models import Q
#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Kvartal, Building, Locker, Cross, Device, Box, Subunit
from .models import Cross_ports, Device_ports, Device_ports_v, Box_ports
from core.models import Templ_locker, Templ_cross, Templ_device, Templ_box_cable, Templ_box, Templ_subunit
from core.models import Device_type, Subunit_type, manage_comp
from cable.models import Coupling

#from .forms import find_Form_dev, find_Form_agr, find_Form_bu
from .forms import new_locker_Form, new_cr_Form, new_dev_Form, new_box_Form, new_su_Form
from .forms import new_dev_p_v_Form, edit_dev_p_v_Form
from .forms import edit_bu_Form, edit_lo_Form
from .forms import edit_cr_p_Form, edit_dev_p_Form, edit_box_p_Form
from .forms import edit_cr_Form, edit_dev_Form, edit_box_Form
from .forms import edit_subunit_Form
#from app_proc.forms import app_find_Form

from core.shared_def import to_his
from core.e_config import conf

####################################################################################################
####################################################################################################


@login_required(login_url='/core/login/')
def new_locker(request, bu_id):

    if not request.user.has_perm("core.can_new"):
        return render(request, 'denied.html', {'mess': 'нет прав для создания УД', 'back': 1})

    bu = Building.objects.get(pk=bu_id)
    if request.method == 'POST':
        form = new_locker_Form(request.POST)
        if form.is_valid():
            locker_type = form.cleaned_data['lo_name_type']
            locker = Templ_locker.objects.get(pk=locker_type)
            locker_name_type = locker.name

            n_locker = Locker.objects.create(parrent_id=bu_id,
                                             name=form.cleaned_data['lo_name'],
                                             name_type=locker_name_type,
                                             con_type=locker_type,
                                             co=form.cleaned_data['co']
                                             )

            to_his([request.user, 1, n_locker.id, 1, 0, 'name: '+n_locker.name])

            n_coup = Coupling.objects.create(parrent=n_locker.id,
                                             parr_type=0,
                                             name=n_locker.name+'-Ш',
                                             name_type='кассета (УД)',
                                             )

            return HttpResponseRedirect(request.get_full_path()+'../')
    else:
        form = new_locker_Form(initial={'kvar': bu.kvar})

    return render(request, 'new.html', {'form': form, 'bu': bu})


@login_required(login_url='/core/login/')
def new_cr(request, bu_id, lo_id):

    if not request.user.has_perm("core.can_new"):
        return render(request, 'denied.html', {'mess': 'нет прав для создания кросса', 'back': 1})

    lo = Locker.objects.get(pk=lo_id)
    if request.method == 'POST':
        form = new_cr_Form(request.POST)
        if form.is_valid():
            cr_type = form.cleaned_data['cr_name_type']
            cr = Templ_cross.objects.get(pk=cr_type)
            with transaction.atomic():
                n_cr = Cross.objects.create(parrent_id=lo_id,
                                            name=form.cleaned_data['cr_name'],
                                            name_type=cr.name,
                                            con_type=cr_type,
                                            v_col=cr.v_col,
                                            v_row=cr.v_row,
                                            v_forw_l_r=cr.v_forw_l_r
                                            )
                i = 0
                while i < cr.ports:
                    i = i + 1
                    Cross_ports.objects.create(parrent_id=n_cr.id,
                                               num=i,
                                               port_t_x=cr.port_t_x,
                                               prim='...'
                                               )
            to_his([request.user, 2, n_cr.id, 1, 0, 'name: '+n_cr.name+', УД: '+n_cr.parrent.name])

            return HttpResponseRedirect(request.get_full_path()+'../')
    else:
        form = new_cr_Form(initial={'cr_name': 'kc-1', 'cr_name_type': 1})

    return render(request, 'new.html', {'form': form, 'lo': lo})


@login_required(login_url='/core/login/')
def new_dev(request, bu_id, lo_id):

    if not request.user.has_perm("core.can_new"):
        return render(request, 'denied.html', {'mess': 'нет прав для создания оборудования', 'back': 1})

    lo = Locker.objects.get(pk=lo_id)
    if request.method == 'POST':
        form = new_dev_Form(request.POST)
        try:    dev_type2 = form.data['dev_name_type2']
        except: dev_type2 = False

        if form.is_valid() and dev_type2:
            dev = Templ_device.objects.get(pk=dev_type2)
            p_al_list = dev.port_alias_list.split(',')
            p_tx_list = dev.port_t_x_list.split(',')
            p_sp_list = dev.port_speed_list.split(',')
            if len(p_al_list) != dev.ports or len(p_tx_list) != dev.ports or len(p_sp_list) != dev.ports:
                return render(request, 'error.html', {'mess': 'ошибка в шаблоне', 'back': 1})
            with transaction.atomic():
                n_dev = Device.objects.create(parrent_id=lo_id,
                                              name=form.cleaned_data['dev_name'],
                                              #name_type=dev.name,       ######## deprecated
                                              con_type=dev.id,          ########
                                              obj_type=dev
                                              )
                i = 0
                while i < dev.ports:
                    i = i + 1
                    Device_ports.objects.create(parrent_id=n_dev.id,
                                                num=i,
                                                port_t_x=p_tx_list[i-1],
                                                port_speed=p_sp_list[i-1],
                                                p_alias=p_al_list[i-1]
                                                #prim='...'
                                                )

            to_his([request.user, 3, n_dev.id, 1, 0, 'name: '+n_dev.name])

            return HttpResponseRedirect(request.get_full_path()+'../')
    else:
        dev_c = Device.objects.filter(parrent_id=lo_id).count()
        form = new_dev_Form(initial={'dev_name': (lo.name+'-'+str(dev_c+1))})#, 'dev_name_type': 2})

    t_list = Templ_device.objects.values('parrent_id', 'id', 'name', 'ports').order_by('parrent_id', 'name')
    i = 0
    dev_type_list = Device_type.objects.all()
    for ob in t_list:
        if ob['parrent_id'] != i:
            i = ob['parrent_id']
            #ob['next_type'] = Device_type.objects.get(pk=ob['parrent_id']).name
            ob['next_type'] = dev_type_list.get(pk=ob['parrent_id']).name
            #ob['count_type'] = Templ_device.objects.filter(parrent_id=i).count()
        else:
            ob['next_type'] = False
            #ob['count_type'] = False

    return render(request, 'new_dev.html', {'form': form,
                                            'lo': lo,
                                            't_list': t_list,
                                            })


@login_required(login_url='/core/login/')
def add_v_port(request, bu_id, lo_id, dev_id):

    try:
        lo = Locker.objects.get(pk=lo_id)
        dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 1})

    if lo.parrent_id != int(bu_id) or dev.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 2})

    if not request.user.has_perm("kpp.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования оборудования', 'back': 2})

    if request.method == 'POST':
        form = new_dev_p_v_Form(request.POST)
        if form.is_valid() and (form.cleaned_data['vlan_untag'].isdecimal() or form.cleaned_data['vlan_untag'] == ''):
            sel_vlan_untag = form.cleaned_data['vlan_untag']
            n_p = Device_ports_v.objects.create(parrent_id=dev.id,
                                                parrent_p=form.cleaned_data['parrent_p'],
                                                p_alias=form.cleaned_data['p_alias'],
                                                prim=form.cleaned_data['prim'],
                                                vlan_untag=sel_vlan_untag,
                                                ip=form.cleaned_data['ip']
                                                )
            
            to_his([request.user, 11, n_p.id, 1, 0, 'УД: '+dev.parrent.name+', dev: '+dev.name+', alias: '+form.cleaned_data['p_alias']])
            
            return HttpResponseRedirect(request.get_full_path()+'../l2=1/')
        else:
            form = new_dev_p_v_Form(initial={'parrent_p': 0,
                                             'p_alias': form.data['p_alias'],
                                             'vlan_untag': form.data['vlan_untag'],
                                             'ip': form.data['ip'],
                                             'prim': form.data['prim'],
                                             })
    else:
        form = new_dev_p_v_Form(initial={'parrent_p': 0})

    return render(request, 'new_v_p.html', {'form': form, 'dev': dev})


@login_required(login_url='/core/login/')
def new_box(request, bu_id, lo_id):

    if not request.user.has_perm("core.can_new"):
        return render(request, 'denied.html', {'mess': 'нет прав для создания крт', 'back': 1})

    lo = Locker.objects.get(pk=lo_id)
    if request.method == 'POST':
        form = new_box_Form(request.POST)
        if form.is_valid():
            cable = Templ_box_cable.objects.get(pk=form.cleaned_data['cable_name_type'])
            box_name = form.cleaned_data['box_name']
            a_list = cable.alias_list.split(',')
            if len(a_list) != cable.ports:
                return render(request, 'error.html', {'mess': 'ошибка в шаблоне', 'back': 1})
            with transaction.atomic():
                n_box = Box.objects.create(parrent_id=lo_id,
                                           name=box_name,
                                           stairway=box_name if (box_name != '0') else '',
                                           num=form.cleaned_data['box_num'],
                                           name_type=Templ_box.objects.get(pk=form.cleaned_data['box_name_type']).name,
                                           con_type=form.cleaned_data['box_name_type'],
                                           num_plints=cable.num_plints
                                           )
                i = 0
                while i < cable.ports:
                    i = i + 1
                    Box_ports.objects.create(parrent_id=n_box.id,
                                             cable_id=cable.id,
                                             num=i,
                                             port_t_x=2,
                                             p_alias=a_list[i-1]
                                             )

            to_his([request.user, 4, n_box.id, 1, 0, 'name: '+n_box.name+'-'+n_box.num+', УД: '+n_box.parrent.name])

            return HttpResponseRedirect(request.get_full_path()+'../')
    else:
        form = new_box_Form(initial={'box_name_type': 'крт 30'})

    return render(request, 'new.html', {'form': form, 'lo': lo})


@login_required(login_url='/core/login/')
def new_su(request, bu_id, lo_id):

    if not request.user.has_perm("core.can_new"):
        return render(request, 'denied.html', {'mess': 'нет прав для создания оборудования', 'back': 1})

    lo = Locker.objects.get(pk=lo_id)
    if request.method == 'POST':
        form = new_su_Form(request.POST)
        try:
            su_type2 = form.data['su_name_type2']
        except:
            su_type2 = False
        if form.is_valid() and su_type2:
            su = Templ_subunit.objects.get(pk=su_type2)
            n_su = Subunit.objects.create(parrent_id=lo_id,
                                          name=form.cleaned_data['su_name'],
                                          con_type=su.id,
                                          )
            h_text = 'УД: '+lo.name+'; name: '+n_su.name+'; type: '+su.name
            to_his([request.user, 13, n_su.id, 1, 0, h_text])
            
            return HttpResponseRedirect('../')
    else:
        su_c = Subunit.objects.filter(parrent_id=lo_id).count()
        form = new_su_Form(initial={'su_name': (lo.name+'-su-'+str(su_c+1))})

    t_list = Templ_subunit.objects.values('parrent_id', 'id', 'name').order_by('parrent_id', 'name')
    i = 0
    for ob in t_list:
        if ob['parrent_id'] != i:
            i = ob['parrent_id']
            ob['next_type'] = Subunit_type.objects.get(pk=ob['parrent_id']).name
            ob['count_type'] = Templ_subunit.objects.filter(parrent_id=i).count()
        else:
            ob['next_type'] = False
            ob['count_type'] = False
    
    return render(request, 'new_su.html', {'form': form,
                                           'lo': lo,
                                           't_list': t_list,
                                           })


####################################################################################################

@login_required(login_url='/core/login/')
def edit_build(request, bu_id):

    if not request.user.has_perm("core.can_edit_bu"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования здания', 'back': 1})

    bu = Building.objects.get(pk=bu_id)

    if request.method == 'POST':
        form = edit_bu_Form(request.POST)
        if form.is_valid():
            change = False
            h_text = 'ЗД: '+bu.name+' '+str(bu.house_num)+'; '

            if form.cleaned_data['kvar'] != str(bu.kvar):
                change = True
                h_text += 'квартал: '+Kvartal.objects.get(pk=bu.kvar).name+' -> '+Kvartal.objects.get(pk=int(form.cleaned_data['kvar'])).name+'; '
                bu.kvar = form.cleaned_data['kvar']

            id_comp = bu.info_comp
            if id_comp == 0: id_comp = 1                        ### debug
            if int(form.cleaned_data['info_comp']) != id_comp:
                change = True
                h_text += 'упр_к: '+manage_comp.objects.get(pk=id_comp).name+' -> '+manage_comp.objects.get(pk=int(form.cleaned_data['info_comp'])).name+'; '
                bu.info_comp = form.cleaned_data['info_comp']
            if form.cleaned_data['info_cont'] != bu.info_cont:
                change = True
                h_text += 'конт_инф: '+bu.info_cont+' -> '+form.cleaned_data['info_cont']+'; '
                bu.info_cont = form.cleaned_data['info_cont']
            if form.cleaned_data['cnt_place'] != bu.cnt_place:
                change = True
                h_text += 'дог_разм: '+bu.cnt_place+' -> '+form.cleaned_data['cnt_place']+'; '
                bu.cnt_place = form.cleaned_data['cnt_place']
            if form.cleaned_data['cnt_price'] != bu.cnt_price:
                change = True
                h_text += 'цена_дог_разм: '+bu.cnt_price+' -> '+form.cleaned_data['cnt_price']+'; '
                bu.cnt_price = form.cleaned_data['cnt_price']

            d_date = bu.deadline
            if d_date is None:
                d_m = 0
                d_d = 0
            else:
                d_m = int(d_date.month)
                d_d = int(d_date.day)
            if form.cleaned_data['deadline_use']:
                if d_m != int(form.cleaned_data['deadline_m']) or d_d != int(form.cleaned_data['deadline_d']):
                    change = True
                    bu.deadline = datetime.datetime(2000, int(form.cleaned_data['deadline_m']), int(form.cleaned_data['deadline_d'])).date()
            else:
                if d_date is not None:
                    change = True
                    bu.deadline = None

            if form.cleaned_data['electricity'] != bu.electricity:
                change = True
                h_text += 'эл/эн: '+bu.electricity+' -> '+form.cleaned_data['electricity']+'; '
                bu.electricity = form.cleaned_data['electricity']
            if form.cleaned_data['info_signs'] != bu.info_signs:
                change = True
                h_text += 'info_signs: '+str(bu.info_signs)+' -> '+str(form.cleaned_data['info_signs'])+'; '
                bu.info_signs = form.cleaned_data['info_signs']
            if form.cleaned_data['senior_home'] != bu.senior_home:
                change = True
                h_text += 'ст_дома: '+bu.senior_home+' -> '+form.cleaned_data['senior_home']+'; '
                bu.senior_home = form.cleaned_data['senior_home']
            if form.cleaned_data['tech_conditions'] != bu.tech_conditions:
                change = True
                h_text += 'тех.усл.: '+bu.tech_conditions+' -> '+form.cleaned_data['tech_conditions']+'; '
                bu.tech_conditions = form.cleaned_data['tech_conditions']
            if form.cleaned_data['access'] != bu.access:
                change = True
                h_text += 'доступ: '+bu.access+' -> '+form.cleaned_data['access']+'; '
                bu.access = form.cleaned_data['access']
            if form.cleaned_data['prim'] != bu.prim:
                change = True
                h_text += 'прим: '+bu.prim+' -> '+form.cleaned_data['prim']+'; '
                bu.prim = form.cleaned_data['prim']

            if change:
                bu.save()
                to_his([request.user, 0, bu.id, 2, 0, h_text])

            return HttpResponseRedirect('../')
    else:
        if bu.deadline:
            deadline_use = True
            deadline_d = bu.deadline.day
            deadline_m = bu.deadline.month
        else:
            deadline_use = False
            deadline_d = False
            deadline_m = False

        form = edit_bu_Form(initial={'kvar': bu.kvar,
                                     'info_comp': bu.info_comp,
                                     'info_cont': bu.info_cont,
                                     'cnt_place': bu.cnt_place,
                                     'cnt_price': bu.cnt_price,
                                     'deadline_use': deadline_use,
                                     'deadline_d': deadline_d,
                                     'deadline_m': deadline_m,
                                     'electricity': bu.electricity,
                                     'info_signs': bu.info_signs,
                                     'senior_home': bu.senior_home,
                                     'tech_conditions': bu.tech_conditions,
                                     'access': bu.access,
                                     'prim': bu.prim,
                                     })

    return render(request, 'edit_bu.html', {'form': form,
                                            'bu': bu,
                                            })


@login_required(login_url='/core/login/')
def edit_locker(request, bu_id, lo_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования УД', 'back': 2})

    lo = Locker.objects.get(pk=lo_id)
    try:
        cab_key1 = lo.cab_key.split('-')[0]
        cab_key2 = lo.cab_key.split('-')[1]
    except:
        cab_key1 = None
        cab_key2 = None

    if request.method == 'POST':
        form = edit_lo_Form(request.POST)
        if form.is_valid():
            change = False
            #sel_status = form.cleaned_data['status']
            if str(lo.status) != form.cleaned_data['status']:
                change = True
                lo.status = form.cleaned_data['status']
            #if form.cleaned_data['date1'] != lo.date_ent:
            #    change = True
            #    lo.date_ent = form.cleaned_data['date1']
            try:
                date2 = datetime.datetime.strptime(form.data['date2'], '%d.%m.%Y').date()
            except:
                date2 = None
            if date2 != lo.date_ent:
                change = True
                lo.date_ent = date2
            if form.cleaned_data['lo_name'] != lo.name:
                change = True
                lo.name = form.cleaned_data['lo_name']
            if form.cleaned_data['lo_name_type'] != str(lo.con_type):
                change = True
                lo.con_type = form.cleaned_data['lo_name_type']
                lo.name_type = Templ_locker.objects.get(pk=form.cleaned_data['lo_name_type']).name
            if form.cleaned_data['object_owner'] != lo.object_owner:
                change = True
                lo.object_owner = form.cleaned_data['object_owner']
            if form.cleaned_data['rasp'] != lo.rasp:
                change = True
                lo.rasp = form.cleaned_data['rasp']
            if form.cleaned_data['prim'] != lo.prim:
                change = True
                lo.prim = form.cleaned_data['prim']
            #if form.cleaned_data['racks'] != lo.racks:
            #    if (len(form.cleaned_data['racks'].split(',')) % 2 == 0) or form.cleaned_data['racks'] == '':
            #        change = True
            #        lo.racks = form.cleaned_data['racks']
            if form.cleaned_data['co'] != lo.co and not lo.agr:
                change = True
                lo.co = form.cleaned_data['co']
            if form.cleaned_data['detached'] != lo.detached:
                change = True
                lo.detached = form.cleaned_data['detached']
            """
            coord_t = form.cleaned_data['coord'].split(',')
            if form.cleaned_data['coord'] != str(round(lo.coord_x))+','+str(round(lo.coord_y)):
                change = True
                try:
                    #c_x = float(coord_t[0])
                    c_x = int(round(float(coord_t[0])))
                    #c_y = float(coord_t[1])
                    c_y = int(round(float(coord_t[1])))
                    coup = Coupling.objects.get(parrent=lo.id, parr_type=0)
                    coup.coord_x = c_x
                    coup.coord_y = c_y
                    coup.save()
                except Exception as e:
                    c_x = 30
                    c_y = 30
                lo.coord_x = c_x
                lo.coord_y = c_y
            """
            if form.cleaned_data['cab_door'] != lo.cab_door:
                change = True
                lo.cab_door = form.cleaned_data['cab_door']
            key_door_ind = conf.KEY_DOOR_TYPE.index(form.cleaned_data['cab_door'])
            if key_door_ind == 1 and form.cleaned_data['cab_key1'] != None and form.cleaned_data['cab_key2'] != None:
                cab_key = str(form.cleaned_data['cab_key1'])+'-'+str(form.cleaned_data['cab_key2'])
                if cab_key != lo.cab_key:
                    change = True
                    lo.cab_key = cab_key

            #if form.cleaned_data['kvar'] != str(lo.parrent.kvar):
            #    change = True
            #    lo.parrent.kvar = form.cleaned_data['kvar']
            #    lo.parrent.save()

            if change:
                lo.save()
                to_his([request.user, 1, lo.id, 2, 0, 'УД: '+lo.name])

            return HttpResponseRedirect('../../')
    else:
        form = edit_lo_Form(initial={'lo_name': lo.name,
                                     'lo_name_type': lo.con_type,
                                     #'date1': lo.date_ent,
                                     'status': lo.status,
                                     'rasp': lo.rasp,
                                     'prim': lo.prim,
                                     #'kvar': lo.parrent.kvar,
                                     'co': lo.co,
                                     'detached': lo.detached,
                                     'coord': str(round(lo.coord_x))+','+str(round(lo.coord_y)),
                                     'racks': lo.racks,
                                     'cab_door': lo.cab_door,
                                     'cab_key1': cab_key1,
                                     'cab_key2': cab_key2,
                                     'object_owner': lo.object_owner,
                                     })
    try:
        date2 = lo.date_ent.strftime('%d.%m.%Y')
    except:
        date2 = ''
    if lo.agr:
        form.fields['co'].disabled = 1
        form.fields['detached'].disabled = 1

    return render(request, 'edit_lo.html', {'form': form,
                                            'lo': lo,
                                            'date2': date2,
                                            })


@login_required(login_url='/core/login/')
def edit_cr(request, bu_id, lo_id, cr_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования кросса', 'back': 2})

    cr = Cross.objects.get(pk=cr_id)

    rack_pos_list = cr.parrent.racks.split(',')
    rack_list = [[0, '---']]
    i = 0
    while i < len(rack_pos_list) / 2:
        rack_list.append([i+1, rack_pos_list[i*2]])
        i += 1

    if request.method == 'POST':
        form = edit_cr_Form(request.POST)
        form.fields['rack_num'].choices = rack_list
        if form.is_valid():
            change = False
            if form.cleaned_data['cr_name'] != cr.name:
                change = True
                cr.name = form.cleaned_data['cr_name']
            if form.cleaned_data['object_owner'] != cr.object_owner:
                change = True
                cr.object_owner = form.cleaned_data['object_owner']
            if form.cleaned_data['prim'] != cr.prim:
                change = True
                cr.prim = form.cleaned_data['prim']

            if form.cleaned_data['ch_type'] == True:
                sou = Templ_cross.objects.get(pk=cr.con_type)
                dst = Templ_cross.objects.get(pk=int(form.cleaned_data['cr_name_type']))
                if sou.ext_p and dst.ext_p:
                    if sou.ports > dst.ports:
                        pass
                    elif sou.ports < dst.ports:
                        with transaction.atomic():
                            i = sou.ports
                            while i < dst.ports:
                                i = i + 1
                                Cross_ports.objects.create(parrent_id=cr_id, num=i, port_t_x=dst.port_t_x, prim='...')
                            cr.name_type = dst.name
                            cr.con_type = dst.id
                            cr.v_col = dst.v_col
                            cr.v_row = dst.v_row
                            cr.v_forw_l_r = dst.v_forw_l_r
                        cr.save()
                        to_his([request.user, 2, cr.id, 11, 0, ''])

            if form.cleaned_data['rack_num'] != cr.rack_num:
                change = True
                #h_text += 'rack_num: '+str(cr.rack_num)+' -> '+str(form.cleaned_data['rack_num'])+'; '
                cr.rack_num = form.cleaned_data['rack_num']
            if form.cleaned_data['rack_pos'] != cr.rack_pos:
                change = True
                #h_text += 'rack_pos: '+str(cr.rack_pos)+' -> '+str(form.cleaned_data['rack_pos'])+'; '
                cr.rack_pos = form.cleaned_data['rack_pos']

            if change:
                cr.save()
                to_his([request.user, 2, cr.id, 2, 0, ''])

            return HttpResponseRedirect('../../')
    else:
        form = edit_cr_Form(initial={'cr_name': cr.name,
                                     'prim': cr.prim,
                                     'cr_name_type': cr.con_type,
                                     'rack_num': cr.rack_num,
                                     'rack_pos': cr.rack_pos,
                                     'object_owner': cr.object_owner,
                                     })

    form.fields['rack_num'].choices = rack_list

    return render(request, 'edit_cr.html', {'form': form, 'cr': cr})


@login_required(login_url='/core/login/')
def edit_cr_p(request, bu_id, lo_id, cr_id, p_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования', 'back': 1})

    s_p = Cross_ports.objects.get(pk=p_id)
    if request.method == 'POST':
        form = edit_cr_p_Form(request.POST)
        if form.is_valid():
            change = False
            if form.cleaned_data['valid'] != s_p.p_valid:
                change = True
                s_p.p_valid = form.cleaned_data['valid']
            if form.cleaned_data['prim'] != s_p.prim:
                change = True
                s_p.prim = form.cleaned_data['prim']
            if form.cleaned_data['opt_len'] != s_p.opt_len:
                change = True
                s_p.opt_len = form.cleaned_data['opt_len'] if str(form.cleaned_data['opt_len']).isdigit else 0
            if s_p.up_status != 0:
                if form.cleaned_data['status1'] != str(s_p.up_status):
                    #change = True
                    s_p.up_status = form.cleaned_data['status1']
                    d_p = Cross_ports.objects.get(pk=s_p.up_cross_id)
                    d_p.up_status = form.cleaned_data['status1']
                    d_p.save()
                    s_p.save()
                    to_his([request.user, 5, d_p.id, 9, 1, ''])
                    to_his([request.user, 5, s_p.id, 9, 1, ''])
            if s_p.int_c_status != 0:
                if form.cleaned_data['status2'] != str(s_p.int_c_status):
                    #change = True
                    s_p.int_c_status = form.cleaned_data['status2']
                    if s_p.int_c_dest == 1:
                        d_p = Cross_ports.objects.get(pk=s_p.int_c_id)
                        #if d_p.int_c_status != s_p.int_c_status: return HttpResponseRedirect('err027')
                        d_p.int_c_status = form.cleaned_data['status2']
                        d_p.save()
                        s_p.save()
                        to_his([request.user, 5, d_p.id, 9, 2, ''])
                        to_his([request.user, 5, s_p.id, 9, 2, ''])
                    if s_p.int_c_dest == 2:
                        d_p = Device_ports.objects.get(pk=s_p.int_c_id)
                        #if d_p.int_c_status != s_p.int_c_status: return HttpResponseRedirect('err028')
                        d_p.int_c_status = form.cleaned_data['status2']
                        d_p.save()
                        s_p.save()
                        to_his([request.user, 6, d_p.id, 9, 0, ''])
                        to_his([request.user, 5, s_p.id, 9, 2, ''])
            if change:
                s_p.save()
                to_his([request.user, 5, s_p.id, 2, 0, ''])

            return HttpResponseRedirect('../')
    else:
        form = edit_cr_p_Form(initial={'valid': s_p.p_valid,
                                       'prim': s_p.prim,
                                       'opt_len': s_p.opt_len,
                                       'status1': s_p.up_status,
                                       'status2': s_p.int_c_status,
                                       })

    return render(request, 'edit_cr_p.html', {'form': form,
                                              'port': s_p,
                                              })


@login_required(login_url='/core/login/')
def edit_dev(request, bu_id, lo_id, dev_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования оборудования', 'back': 2})

    dev = Device.objects.get(pk=dev_id)
    #rack_pos = dev.rack_pos.split(',') if dev.rack_pos != '' else ['', '']
    #rack_pos = dev.rack_pos.split(',') if len(dev.rack_pos) > 2 else ['', '']
    rack_pos_list = dev.parrent.racks.split(',')
    rack_list = [[0, '---']]
    i = 0
    while i < len(rack_pos_list) / 2:
        rack_list.append([i+1, rack_pos_list[i*2]])
        #max_unit = int(rack_pos_list[i*2+1]) if int(rack_pos_list[i*2+1]) > max_unit else max_unit
        i += 1
    if request.method == 'POST':
        form = edit_dev_Form(request.POST)
        form.fields['rack_num'].choices = rack_list
        if form.is_valid():
            change = False
            h_text = 'комм: '+dev.name+'; '
            if form.cleaned_data['dev_name'] != dev.name:
                change = True
                h_text += 'name: '+dev.name+' -> '+form.cleaned_data['dev_name']+'; '
                dev.name = form.cleaned_data['dev_name']
            if form.cleaned_data['object_owner'] != dev.object_owner:
                change = True
                h_text += 'own: '+dev.object_owner+' -> '+form.cleaned_data['object_owner']+'; '
                dev.object_owner = form.cleaned_data['object_owner']
            ip = form.cleaned_data['ip'] if form.cleaned_data['ip'] != '' else None
            if ip != dev.ip_addr:
                if Device.objects.filter(ip_addr=ip).exclude(pk=dev_id).exists():
                    return render(request, 'error.html', {'mess': 'ip адрес уже существует в базе', 'back': 0})
                change = True
                h_text += 'ip: '+str(dev.ip_addr)+' -> '+form.cleaned_data['ip']+'; '
                dev.ip_addr = ip
            mac = form.cleaned_data['mac']
            if mac != dev.mac_addr:
                if (re.match(conf.MAC_RE, mac) and len(mac) == 17) or mac == '':
                    change = True
                    h_text += 'mac: '+dev.mac_addr+' -> '+mac+'; '
                    dev.mac_addr = mac.replace('-', ':').upper()     #.lower()
            if form.cleaned_data['sn'] != dev.sn:
                change = True
                h_text += 'sn: '+dev.sn+' -> '+form.cleaned_data['sn']+'; '
                dev.sn = form.cleaned_data['sn']
            if form.cleaned_data['vers_po'] != dev.vers_po:
                change = True
                h_text += 'vers_po: '+dev.vers_po+' -> '+form.cleaned_data['vers_po']+'; '
                dev.vers_po = form.cleaned_data['vers_po']
            if form.cleaned_data['man_conf'] != dev.man_conf:
                change = True
                h_text += 'man_conf: '+dev.man_conf+' -> '+form.cleaned_data['man_conf']+'; '
                dev.man_conf = form.cleaned_data['man_conf']
            if form.cleaned_data['man_install'] != dev.man_install:
                change = True
                h_text += 'man_install: '+dev.man_install+' -> '+form.cleaned_data['man_install']+'; '
                dev.man_install = form.cleaned_data['man_install']
            if form.cleaned_data['date_ent'] != dev.date_ent:
                change = True
                h_text += 'date_ent: changed; '
                #h_text += 'date_ent: '+str(dev.date_ent)+' -> '+form.cleaned_data['date_ent']+'; '
                dev.date_ent = form.cleaned_data['date_ent']
            if form.cleaned_data['date_repl'] != dev.date_repl:
                change = True
                h_text += 'date_repl: changed; '
                dev.date_repl = form.cleaned_data['date_repl']
            if form.cleaned_data['prim'] != dev.prim:
                change = True
                h_text += 'prim: '+dev.prim+' -> '+form.cleaned_data['prim']+'; '
                dev.prim = form.cleaned_data['prim']
            if form.cleaned_data['rack_num'] != str(dev.rack_num):
                change = True
                h_text += 'rack_num: '+str(dev.rack_num)+' -> '+str(form.cleaned_data['rack_num'])+'; '
                dev.rack_num = form.cleaned_data['rack_num']
            if form.cleaned_data['rack_pos'] != dev.rack_pos:
                change = True
                h_text += 'rack_pos: '+str(dev.rack_pos)+' -> '+str(form.cleaned_data['rack_pos'])+'; '
                dev.rack_pos = form.cleaned_data['rack_pos']

            if change:
                dev.save()
                to_his([request.user, 3, dev.id, 2, 0, h_text])

            return HttpResponseRedirect('../../')
    else:
        form = edit_dev_Form(initial={'dev_name': dev.name,
                                      'ip': dev.ip_addr,
                                      'mac': dev.mac_addr,
                                      'sn': dev.sn,
                                      'vers_po': dev.vers_po,
                                      'date_ent': dev.date_ent,
                                      'date_repl': dev.date_repl,
                                      'man_conf': dev.man_conf,
                                      'man_install': dev.man_install,
                                      'prim': dev.prim,
                                      'rack_num': dev.rack_num,
                                      'rack_pos': dev.rack_pos,
                                      'object_owner': dev.object_owner,
                                      })

    form.fields['rack_num'].choices = rack_list

    return render(request, 'edit_dev.html', {'form': form, 'dev': dev})


@login_required(login_url='/core/login/')
def edit_dev_p(request, bu_id, lo_id, dev_id, p_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования оборудования', 'back': 1})

    try:
        s_p = Device_ports.objects.get(pk=p_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 1})

    if request.method == 'POST':
        form = edit_dev_p_Form(request.POST)
        if form.is_valid():
            change = False
            if form.cleaned_data['valid'] != s_p.p_valid:
                change = True
                s_p.p_valid = form.cleaned_data['valid']
            if form.cleaned_data['alias'] != s_p.p_alias:
                change = True
                s_p.p_alias = form.cleaned_data['alias']
            if form.cleaned_data['prim'] != s_p.prim:
                change = True
                s_p.prim = form.cleaned_data['prim']
            if form.cleaned_data['uplink'] != s_p.uplink:
                change = True
                s_p.uplink = form.cleaned_data['uplink']

            if s_p.int_c_status != 0:
                if form.cleaned_data['status'] != str(s_p.int_c_status):
                    s_p.int_c_status = form.cleaned_data['status']
                    if s_p.int_c_dest == 1:
                        d_p = Cross_ports.objects.get(pk=s_p.int_c_id)
                        #if d_p.int_c_status != s_p.int_c_status: return HttpResponseRedirect('err027')
                        d_p.int_c_status = form.cleaned_data['status']
                        d_p.save()
                        s_p.save()
                        to_his([request.user, 5, d_p.id, 9, 2, ''])
                        to_his([request.user, 6, s_p.id, 9, 0, ''])
                    if s_p.int_c_dest == 2:
                        d_p = Device_ports.objects.get(pk=s_p.int_c_id)
                        #if d_p.int_c_status != s_p.int_c_status: return HttpResponseRedirect('err028')
                        d_p.int_c_status = form.cleaned_data['status']
                        d_p.save()
                        s_p.save()
                        to_his([request.user, 6, d_p.id, 9, 0, ''])
                        to_his([request.user, 6, s_p.id, 9, 0, ''])
                    if s_p.int_c_dest == 3:
                        d_p = Box_ports.objects.get(pk=s_p.int_c_id)
                        #if d_p.int_c_status != s_p.int_c_status: return HttpResponseRedirect('err028')
                        d_p.up_status = form.cleaned_data['status']
                        d_p.save()
                        s_p.save()
                        to_his([request.user, 7, d_p.id, 9, 1, ''])
                        to_his([request.user, 6, s_p.id, 9, 0, ''])

            if change:
                s_p.save()
                to_his([request.user, 6, s_p.id, 2, 0, ''])
            return HttpResponseRedirect('../')
    else:
        form = edit_dev_p_Form(initial={'valid': s_p.p_valid,
                                        'alias': s_p.p_alias,
                                        'prim': s_p.prim,
                                        'status': s_p.int_c_status,
                                        'uplink': s_p.uplink,
                                        })

    return render(request, 'edit_dev_p.html', {'form': form,
                                               'port': s_p,
                                               })


@login_required(login_url='/core/login/')
def edit_dev_p_v(request, bu_id, lo_id, dev_id, f_p_id=None, v_p_id=None):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования оборудования', 'back': 1})

    if f_p_id:
        curr_id = f_p_id
        curr_model = 'Device_ports'
    elif v_p_id:
        curr_id = v_p_id
        curr_model = 'Device_ports_v'
    try:
        port = eval(curr_model).objects.get(pk=curr_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 1})

    if request.method == 'POST':
        form = edit_dev_p_v_Form(request.POST)
        if form.is_valid():
            change = False
            h_text = 'комм: '+port.parrent.name+'; '
            if v_p_id:
                if form.cleaned_data['parrent_p'] != port.parrent_p:
                    change = True
                    h_text += 'parrent_p: '+str(port.parrent_p)+' -> '+str(form.cleaned_data['parrent_p'])+'; '
                    port.parrent_p = form.cleaned_data['parrent_p']
            if form.cleaned_data['p_alias'] != port.p_alias:
                change = True
                h_text += 'p_alias: '+port.p_alias+' -> '+form.cleaned_data['p_alias']+'; '
                port.p_alias = form.cleaned_data['p_alias']
            if form.cleaned_data['desc'] != port.desc:
                change = True
                h_text += 'desc: '+port.desc+' -> '+form.cleaned_data['desc']+'; '
                port.desc = form.cleaned_data['desc']
            if f_p_id:
                if form.cleaned_data['vlan_tag_list'] != port.vlan_tag_list:
                    change = True
                    h_text += 'vlan_tag_list: '+port.vlan_tag_list+' -> '+form.cleaned_data['vlan_tag_list']+'; '
                    port.vlan_tag_list = form.cleaned_data['vlan_tag_list']
                if form.cleaned_data['mvr'] != port.mvr:
                    change = True
                    h_text += 'mvr: '+port.mvr+' -> '+form.cleaned_data['mvr']+'; '
                    port.mvr = form.cleaned_data['mvr']
            if form.cleaned_data['vlan_untag'] != port.vlan_untag:
                change = True
                h_text += 'vlan_untag: '+str(port.vlan_untag)+' -> '+form.cleaned_data['vlan_untag']+'; '
                port.vlan_untag = form.cleaned_data['vlan_untag']

            if form.cleaned_data['ip'] != port.ip:
                change = True
                h_text += 'ip: '+port.ip+' -> '+form.cleaned_data['ip']+'; '
                port.ip = form.cleaned_data['ip']
            if form.cleaned_data['shut'] != port.shut:
                change = True
                h_text += 'shut: '+str(port.shut)+' -> '+str(form.cleaned_data['shut'])+'; '
                port.shut = form.cleaned_data['shut']
            if form.cleaned_data['prim'] != port.prim:
                change = True
                h_text += 'prim: '+port.prim+' -> '+form.cleaned_data['prim']+'; '
                port.prim = form.cleaned_data['prim']

            if change:
                port.save()
                to_his([request.user, 11 if v_p_id else 6, port.id, 2, 0, h_text])

            return HttpResponseRedirect('../l2=1/')

    form = edit_dev_p_v_Form(initial={'parrent_p': port.parrent_p if v_p_id else 0,
                                      'p_alias': port.p_alias,
                                      'vlan_tag_list': port.vlan_tag_list if f_p_id else False,
                                      'mvr': port.mvr if f_p_id else False,
                                      'vlan_untag': port.vlan_untag if port.vlan_untag != 0 else '',
                                      'ip': port.ip,
                                      'shut': port.shut,
                                      'desc': port.desc,
                                      'prim': port.prim,
                                      })

    return render(request, 'edit_dev_p_v.html', {'form': form,
                                                 'port': port,
                                                 'vlan_tag_list': True if f_p_id else False,
                                                 'parrent_p': True if v_p_id else False,
                                                })


@login_required(login_url='/core/login/')
def edit_box(request, bu_id, lo_id, box_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования крт', 'back': 2})

    box = Box.objects.get(pk=box_id)

    rack_pos_list = box.parrent.racks.split(',')
    rack_list = [[0, '---']]
    i = 0
    while i < len(rack_pos_list) / 2:
        rack_list.append([i+1, rack_pos_list[i*2]])
        i += 1

    if request.method == 'POST':
        form = edit_box_Form(request.POST)
        form.fields['rack_num'].choices = rack_list
        if form.is_valid():
            change = False
            h_text = 'УД: '+box.parrent.name+'; крт: '+box.name+'-'+box.num+'; '
            if form.cleaned_data['box_name'] != box.name:
                change = True
                h_text += 'name: '+box.name+' -> '+form.cleaned_data['box_name']+'; '
                box.name = form.cleaned_data['box_name']
            if form.cleaned_data['box_num'] != box.num:
                change = True
                h_text += 'num: '+box.num+' -> '+form.cleaned_data['box_num']+'; '
                box.num = form.cleaned_data['box_num']
            if form.cleaned_data['box_name_type'] != str(box.con_type):
                change = True
                h_text += 'name_type: '+str(box.con_type)+' -> '+form.cleaned_data['box_name_type']+'; '
                box.con_type = form.cleaned_data['box_name_type']
                box.name_type = Templ_box.objects.get(pk=int(form.cleaned_data['box_name_type'])).name
            if form.cleaned_data['box_stairway'] != box.stairway:
                change = True
                h_text += 'stairway: '+box.stairway+' -> '+form.cleaned_data['box_stairway']+'; '
                box.stairway = form.cleaned_data['box_stairway']
            if form.cleaned_data['floor'] != box.floor:
                change = True
                h_text += 'floor: '+box.floor+' -> '+form.cleaned_data['floor']+'; '
                box.floor = form.cleaned_data['floor']
            if form.cleaned_data['serv_area'] != box.serv_area:
                change = True
                h_text += 'serv_area: '+box.serv_area+' -> '+form.cleaned_data['serv_area']+'; '
                box.serv_area = form.cleaned_data['serv_area']
            if form.cleaned_data['prim'] != box.prim:
                change = True
                h_text += 'prim: '+box.prim+' -> '+form.cleaned_data['prim']+'; '
                box.prim = form.cleaned_data['prim']

            if form.cleaned_data['add_cable'] is True:
                cable_type = form.cleaned_data['cable_name_type']
                if cable_type.isdigit():
                    cable = Templ_box_cable.objects.get(pk=cable_type)
                    a_list = cable.alias_list.split(',')
                    #print(a_list)                   ########
                    if len(a_list) != cable.ports:
                        return render(request, 'error.html', {'mess': 'ошибка в шаблоне', 'back': 2})
                    source_box_p = Box_ports.objects.filter(parrent_id=box.id).order_by('num')
                    source_num_p = source_box_p.count()
                    source_pl = 0
                    source_p_utp = 0
                    source_utp = False
                    for i in source_box_p:
                        if not i.p_alias[0].isdigit():
                            source_utp = True
                            source_p_utp += 1
                        else:
                            if int(i.p_alias[0]) > source_pl:
                                source_pl = int(i.p_alias[0])
                    #print(source_p_utp)                   ########
                    dest_pl = cable.num_plints
                    dest_utp = False
                    for i in range(len(a_list)):
                        al = a_list[i]
                        al0 = al[al.find('('):al.find(')')][1:].split('-')
                        #print(al)                   ########
                        #print(al0)                   ########
                        if not al[0].isdigit():
                            dest_utp = True
                            #a_list[i] = 'u-('+str(source_p_utp*2+int(al[3]))+'-'+str(source_p_utp*2+int(al[5]))+')'
                            a_list[i] = 'u-('+str(source_p_utp*2+int(al0[0]))+'-'+str(source_p_utp*2+int(al0[1]))+')'
                            #print('u-('+str(source_p_utp*2+int(al0[0]))+'-'+str(source_p_utp*2+int(al0[1]))+')')
                            #print(str(source_p_utp*2+int(al[3])))                   ########
                            #print(str(source_p_utp*2+int(al[5])))                   ########
                        else:
                            a_list[i] = str(int(al[0])+source_pl)+al[1:]

                    num_pl = box.num_plints+dest_pl
                    if source_utp and dest_utp:
                        num_pl -= 1
                    if num_pl > 9:
                        return render(request, 'error.html', {'mess': 'ограничение на количество плинтов (>9)', 'back': 2})
                    box.num_plints = num_pl

                    with transaction.atomic():
                        i = 0
                        while i < cable.ports:
                            i = i + 1
                            Box_ports.objects.create(parrent_id=box.id,
                                                     cable_id=cable.id,
                                                     num=source_num_p+i,
                                                     port_t_x=2,
                                                     p_alias=a_list[i-1]
                                                     )
                    #box.save()
                    change = True
                    to_his([request.user, 4, box.id, 10, cable_type, 'УД: '+box.parrent.name+'; крт: '+box.name+'-'+box.num])
            
            elif form.cleaned_data['del_cable'] is True:        # delete last cable from box
                all_b_p = Box_ports.objects.filter(parrent_id=box_id).order_by('-num')
                cable = Templ_box_cable.objects.get(pk=all_b_p.first().cable_id)
                #cab_b_p = all_b_p[:cable.ports]
                ok = True
                del_utp = False
                box_utp = False
                np_list = []
                id_list = []
                for ob in all_b_p[:cable.ports]:
                    #print(ob.p_alias)
                    if ob.up_status != 0 or ob.int_c_status != 0:
                        ok = False
                    if not ob.p_alias[:1].isdigit():
                        del_utp = True
                    else:
                        np_list.append(ob.p_alias[:1])
                    id_list.append(ob.id)
                del_plint = len(list(set(np_list)))
                
                for ob in all_b_p[cable.ports:]:
                    if not ob.p_alias[:1].isdigit():
                        box_utp = True
                #print(box_utp)
                #print(id_list)
                if ok and request.user.has_perm("kpp.can_adm"):
                    change = True
                    del_count = all_b_p.filter(id__in=id_list).delete()
                    #print('box.num_plints')
                    #print(box.num_plints)
                    if del_utp and not box_utp:
                        del_plint += 1
                    box.num_plints = box.num_plints - del_plint
                    #print('box.num_plints')
                    #print(box.num_plints)
                    #print(del_count)

            if form.cleaned_data['rack_num'] != str(box.rack_num):
                change = True
                h_text += 'rack_num: '+str(box.rack_num)+' -> '+str(form.cleaned_data['rack_num'])+'; '
                box.rack_num = form.cleaned_data['rack_num']
            if form.cleaned_data['rack_pos'] != box.rack_pos:
                change = True
                h_text += 'rack_pos: '+str(box.rack_pos)+' -> '+str(form.cleaned_data['rack_pos'])+'; '
                box.rack_pos = form.cleaned_data['rack_pos']

            if change:
                box.save()
                to_his([request.user, 4, box.id, 2, 0, h_text])

            return HttpResponseRedirect('../../')
    else:
        form = edit_box_Form(initial={'box_name_type': box.con_type,
                                      'box_name': box.name,
                                      'box_num': box.num,
                                      'box_stairway': box.stairway,
                                      'floor': box.floor,
                                      'serv_area': box.serv_area,
                                      'prim': box.prim,
                                      'cable_name_type': 0,
                                      'rack_num': box.rack_num,
                                      'rack_pos': box.rack_pos
                                      })

    form.fields['rack_num'].choices = rack_list

    return render(request, 'edit_box.html', {'form': form,
                                             'box': box,
                                             })


@login_required(login_url='/core/login/')
def edit_box_p(request, bu_id, lo_id, box_id, p_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования крт', 'back': 1})

    s_p = Box_ports.objects.get(pk=p_id)
    if request.method == 'POST':
        form = edit_box_p_Form(request.POST)
        if form.is_valid():
            change = False
            h_text = 'УД: '+s_p.parrent.parrent.name+'; крт: '+s_p.parrent.name+'-'+s_p.parrent.num+'-'+s_p.p_alias+'; '
            if s_p.up_status != 0:
                if form.cleaned_data['status1'] != str(s_p.up_status):
                    s_p.up_status = form.cleaned_data['status1']
                    d_p = Device_ports.objects.get(pk=s_p.up_device_id)
                    d_p.int_c_status = form.cleaned_data['status1']
                    d_p.save()
                    s_p.save()
                    to_his([request.user, 6, d_p.id, 9, 0, h_text+'int_c_status_to: '+form.cleaned_data['status1']])
                    to_his([request.user, 7, s_p.id, 9, 1, h_text+'up_status_to: '+form.cleaned_data['status1']])
            if s_p.int_c_status != 0:
                if form.cleaned_data['status2'] != str(s_p.int_c_status):
                    s_p.int_c_status = form.cleaned_data['status2']
                    s_p.save()
                    to_his([request.user, 7, s_p.id, 9, 2, h_text+'int_c_status_to: '+form.cleaned_data['status2']])
            if request.user.has_perm("kpp.can_adm"):
                if form.cleaned_data['dog'] != s_p.dogovor and form.cleaned_data['dog'] != '':
                    change = True
                    h_text += 'dogovor: '+s_p.dogovor+' -> '+form.cleaned_data['dog']+'; '
                    s_p.dogovor = form.cleaned_data['dog'].strip()
            if form.cleaned_data['valid'] != s_p.p_valid:
                change = True
                h_text += 'valid: '+str(s_p.p_valid)+' -> '+str(form.cleaned_data['valid'])+'; '
                s_p.p_valid = form.cleaned_data['valid']
            if form.cleaned_data['kv'] != s_p.ab_kv:
                change = True
                h_text += 'ab_kv: '+s_p.ab_kv+' -> '+form.cleaned_data['kv']+'; '
                s_p.ab_kv = form.cleaned_data['kv']
            if form.cleaned_data['fio'] != s_p.ab_fio:
                change = True
                h_text += 'ab_fio: '+s_p.ab_fio+' -> '+form.cleaned_data['fio']+'; '
                s_p.ab_fio = form.cleaned_data['fio']
            if form.cleaned_data['prim'] != s_p.ab_prim:
                change = True
                h_text += 'ab_prim: '+s_p.ab_prim+' -> '+form.cleaned_data['prim']+'; '
                s_p.ab_prim = form.cleaned_data['prim']
            if form.cleaned_data['h_dog'] != s_p.his_dogovor:
                change = True
                h_text += 'h_dog: '+s_p.his_dogovor+' -> '+form.cleaned_data['h_dog']+'; '
                s_p.his_dogovor = form.cleaned_data['h_dog']
            if form.cleaned_data['h_kv'] != s_p.his_ab_kv:
                change = True
                h_text += 'h_kv: '+s_p.his_ab_kv+' -> '+form.cleaned_data['h_kv']+'; '
                s_p.his_ab_kv = form.cleaned_data['h_kv']
            if form.cleaned_data['h_fio'] != s_p.his_ab_fio:
                change = True
                h_text += 'h_fio: '+s_p.his_ab_fio+' -> '+form.cleaned_data['h_fio']+'; '
                s_p.his_ab_fio = form.cleaned_data['h_fio']
            if form.cleaned_data['h_prim'] != s_p.his_ab_prim:
                change = True
                h_text += 'h_prim: '+s_p.his_ab_prim+' -> '+form.cleaned_data['h_prim']+'; '
                s_p.his_ab_prim = form.cleaned_data['h_prim']
            if form.cleaned_data['changed'] != s_p.changed:
                change = True
                h_text += 'changed: '+str(s_p.changed)+' -> '+str(form.cleaned_data['changed'])+'; '
                s_p.changed = form.cleaned_data['changed']

            if change:
                s_p.save()
                to_his([request.user, 7, s_p.id, 2, 0, h_text])

            return HttpResponseRedirect('../?sel=' + str(p_id))
    else:
        form = edit_box_p_Form(initial={'valid': s_p.p_valid,
                                        'changed': s_p.changed,
                                        'status1': s_p.up_status,
                                        'status2': s_p.int_c_status,
                                        'dog': s_p.dogovor,
                                        'kv': s_p.ab_kv,
                                        'fio': s_p.ab_fio,
                                        'prim': s_p.ab_prim,
                                        'h_dog': s_p.his_dogovor,
                                        'h_kv': s_p.his_ab_kv,
                                        'h_fio': s_p.his_ab_fio,
                                        'h_prim': s_p.his_ab_prim
                                        })

    return render(request, 'edit_box_p.html', {'form': form,
                                               'port': s_p,
                                               })


@login_required(login_url='/core/login/')
def edit_subunit(request, bu_id, lo_id, su_id):

    if not request.user.has_perm("core.can_edit"):
        return render(request, 'denied.html', {'mess': 'нет прав для редактирования оборудования', 'back': 2})
    
    lo = Locker.objects.get(pk=lo_id)
    su = Subunit.objects.get(pk=int(su_id)) if (su_id != '0') else 0
    
    if request.method == 'POST':
        form = edit_subunit_Form(request.POST)
        if form.is_valid():
            h_text = ''
            if True: ####
                change = False
                if form.cleaned_data['name'] != su.name:
                    change = True
                    h_text += 'name: '+su.name+' -> '+form.cleaned_data['name']+'; '
                    su.name = form.cleaned_data['name']
                if form.cleaned_data['object_owner'] != su.object_owner:
                    change = True
                    h_text += 'own: '+su.object_owner+' -> '+form.cleaned_data['object_owner']+'; '
                    su.object_owner = form.cleaned_data['object_owner']
                if form.cleaned_data['name_type'] != str(su.con_type):
                    change = True
                    h_text += 'name_type: '+str(su.con_type)+' -> '+form.cleaned_data['name_type']+'; '
                    su.con_type = int(form.cleaned_data['name_type'])
                if form.cleaned_data['poe'] != str(su.poe):
                    change = True
                    h_text += 'poe: '+str(su.poe)+' -> '+form.cleaned_data['poe']+'; '
                    su.poe = int(form.cleaned_data['poe'])
                if form.cleaned_data['ip'] != su.ip_addr:
                    change = True
                    h_text += 'ip: '+str(su.ip_addr)+' -> '+form.cleaned_data['ip']+'; '
                    su.ip_addr = form.cleaned_data['ip']
                mac = form.cleaned_data['mac']
                if mac != su.mac_addr:
                    if re.match(conf.MAC_RE, mac) and len(mac) == 17:
                        change = True
                        h_text += 'mac: '+su.mac_addr+' -> '+mac+'; '
                        su.mac_addr = mac.replace('-', ':').upper()
                if form.cleaned_data['sn'] != su.sn:
                    change = True
                    h_text += 'sn: '+su.sn+' -> '+form.cleaned_data['sn']+'; '
                    su.sn = form.cleaned_data['sn']
                if form.cleaned_data['inv'] != su.inv:
                    change = True
                    h_text += 'inv: '+su.inv+' -> '+form.cleaned_data['inv']+'; '
                    su.inv = form.cleaned_data['inv']
                if form.cleaned_data['man_install'] != su.man_install:
                    change = True
                    h_text += 'man_install: '+su.man_install+' -> '+form.cleaned_data['man_install']+'; '
                    su.man_install = form.cleaned_data['man_install']
                if form.cleaned_data['date_ent'] != su.date_ent:
                    change = True
                    h_text += 'date_ent: changed; '
                    su.date_ent = form.cleaned_data['date_ent']
                if form.cleaned_data['date_repl'] != su.date_repl:
                    change = True
                    h_text += 'date_repl: changed; '
                    su.date_repl = form.cleaned_data['date_repl']
                if form.cleaned_data['stairway'] != su.stairway:
                    change = True
                    h_text += 'stairway: '+su.stairway+' -> '+form.cleaned_data['stairway']+'; '
                    su.stairway = form.cleaned_data['stairway']
                if form.cleaned_data['floor'] != su.floor:
                    change = True
                    h_text += 'floor: '+su.floor+' -> '+form.cleaned_data['floor']+'; '
                    su.floor = form.cleaned_data['floor']
                if form.cleaned_data['prim'] != su.prim:
                    change = True
                    h_text += 'prim: '+su.prim+' -> '+form.cleaned_data['prim']+'; '
                    su.prim = form.cleaned_data['prim']

                if change:
                    su.save()
                    to_his([request.user, 13, su.id, 2, 0, h_text])
            
            return HttpResponseRedirect('../')
    
    else:
        su_f = {}
        if su:
            su_f['name'] = su.name
            su_f['object_owner'] = su.object_owner
            su_f['name_type'] = su.con_type#Templ_subunit.objects.get(pk=su.con_type).name#conf.SUBUNIT_TYPE[su.con_type]
            su_f['poe'] = conf.POE_TYPE[su.poe]
            su_f['ip'] = su.ip_addr# if su.ip_addr != None else ''
            su_f['mac'] = su.mac_addr
            su_f['sn'] = su.sn
            su_f['inv'] = su.inv
            su_f['man_install'] = su.man_install
            su_f['date_ent'] = su.date_ent
            su_f['date_repl'] = su.date_repl
            su_f['stairway'] = su.stairway
            su_f['floor'] = su.floor
            su_f['prim'] = su.prim
    
        form = edit_subunit_Form(initial=su_f)
    
    return render(request, 'edit_subunit.html', {'form': form,
                                                 'lo': lo,
                                                 'su': su,
                                                 })
    

#############################################################################################################################
#############################################################################################################################

@login_required(login_url='/core/login/')
def del_cross(request, bu_id, lo_id, cr_id):

    try:
        lo = Locker.objects.get(pk=lo_id)
        cr = Cross.objects.get(pk=cr_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id) or cr.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if not request.user.has_perm("core.can_del"):
        return render(request, 'denied.html', {'mess': 'нет прав для удаления',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
                                               })

    del_ok = False if Cross_ports.objects.filter(parrent=cr.id).exclude(up_status=0, int_c_status=0, cab_p_id=0).count() != 0 else True
    if request.method == 'POST' and del_ok:

        to_his([request.user, 1, lo.id, 13, 0, 'cross name: '+cr.name])
        cr.delete()

        return HttpResponseRedirect(request.get_full_path()+'../')

    return render(request, 'del.html', {'cr': cr,
                                        'del_ok': del_ok,
                                        })


@login_required(login_url='/core/login/')
def del_dev(request, bu_id, lo_id, dev_id):

    try:
        lo = Locker.objects.get(pk=lo_id)
        dev = Device.objects.get(pk=dev_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id) or dev.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if not request.user.has_perm("core.can_del"):
        return render(request, 'denied.html', {'mess': 'нет прав для удаления',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
                                               })

    del_ok = False if Device_ports.objects.filter(parrent=dev.id).exclude(int_c_status=0).count() != 0 else True
    if request.method == 'POST' and del_ok:

        to_his([request.user, 1, lo.id, 13, 0, 'dev name: '+dev.name])
        dev.delete()

        return HttpResponseRedirect(request.get_full_path()+'../')

    return render(request, 'del.html', {'dev': dev,
                                        'del_ok': del_ok,
                                        })


@login_required(login_url='/core/login/')
def del_v_port(request, bu_id, lo_id, dev_id, v_p_id):

    try:
        lo = Locker.objects.get(pk=lo_id)
        dev = Device.objects.get(pk=dev_id)
        v_p = Device_ports_v.objects.get(pk=v_p_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id) or dev.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if not request.user.has_perm("core.can_del"):
        return render(request, 'denied.html', {'mess': 'нет прав для удаления',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
                                               })
    if request.method == 'POST':

        to_his([request.user, 3, dev.id, 13, 0, 'v_port alias: '+v_p.p_alias])
        v_p.delete()

        return HttpResponseRedirect(request.get_full_path()+'../l2=1/')

    return render(request, 'del_v_p.html', {'v_p': v_p,})


@login_required(login_url='/core/login/')
def del_box(request, bu_id, lo_id, box_id):

    try:
        lo = Locker.objects.get(pk=lo_id)
        box = Box.objects.get(pk=box_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id) or box.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if not request.user.has_perm("core.can_del"):
        return render(request, 'denied.html', {'mess': 'нет прав для удаления',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
                                               })

    del_ok = False if Box_ports.objects.filter(parrent=box.id).exclude(up_status=0, int_c_status=0).count() != 0 else True
    if request.method == 'POST' and del_ok:

        to_his([request.user, 1, lo.id, 13, 0, 'box name: '+box.name+'-'+box.num])
        box.delete()

        return HttpResponseRedirect(request.get_full_path()+'../')

    return render(request, 'del.html', {'box': box,
                                        'del_ok': del_ok,
                                        })


@login_required(login_url='/core/login/')
def del_subunit(request, bu_id, lo_id, su_id):

    try:
        lo = Locker.objects.get(pk=lo_id)
        su = Subunit.objects.get(pk=su_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 2})

    if lo.parrent_id != int(bu_id) or su.parrent_id != int(lo_id):
        return render(request, 'error.html', {'mess': 'несоответствие вложенных контейнеров', 'back': 3})

    if not request.user.has_perm("core.can_del"):
        return render(request, 'denied.html', {'mess': 'нет прав для удаления',
                                               'back': 1,
                                               'next_url': '/cross/build='+bu_id+'/locker='+lo_id+'/'
                                               })

    del_ok = False if su.box_p_id != 0 else True
    if request.method == 'POST' and del_ok:

        to_his([request.user, 1, lo.id, 13, 0, 'su name: '+su.name])
        su.delete()

        return HttpResponseRedirect(request.get_full_path()+'../')

    return render(request, 'del.html', {'su': su,
                                        'del_ok': del_ok,
                                        })


####################################################################################################
