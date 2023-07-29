# cable__views

import datetime

from django.shortcuts import render
#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import PW_cont, Coupling, Coupling_ports
from .models import Templ_cable
from cross.models import Kvartal, Building, Locker, Cross
from cross.models import Cross_ports
from core.models import firm

from find.forms import find_Form_kv
from .forms import add_PW_Form, add_Coup_Form
from .forms import coup_link_Form
from .forms import coup_p_edit_Form, coup_cab_edit_Form

from core.shared_def import chain_trace, find_coup_parrent, upd_visit, to_his
from core.e_config import conf

from .vols_def import vols_coup_move, vols_cab_up, vols_cab_remove

##########################################################################################

@login_required(login_url='/core/login/')
def cable_main(request):
    
    upd_visit(request.user, 'cab_m')

    if request.method == 'POST':
        form = find_Form_kv(request.POST)
        if form.is_valid():
            kvar = form.cleaned_data['kvar']
    else:
        try:
            kvar = request.GET['kv']
        except:
            kvar = 0

    obj_list = create_obj_list(kvar)
    form = find_Form_kv(initial={'kvar': kvar})

    return render(request, 'cable_main.html', {
                                                'form': form,
                                                'kvar': kvar,
                                                'list1': obj_list[0],
                                                'list2': obj_list[1],
                                                })

#___________________________________________________________________________


def create_obj_list(kvar):

    list1 = []
    list2 = []
    qs1 = Building.objects.filter(kvar=kvar).order_by('name', 'house_num')
    qs2 = PW_cont.objects.filter(parrent=kvar).order_by('obj_type', 'name')
    for ob in qs1:
        coup_list = Coupling.objects.filter(parr_type=1, parrent=ob.id).order_by('name')
        lo_list = Locker.objects.filter(parrent_id=ob.id).order_by('-agr', 'name')
        lo_ob = []
        for lo in lo_list:
            lo_coup = Coupling.objects.filter(parr_type=0, parrent=lo.id).order_by('name').first()
            lo_ob.append([
                            lo.name,
                            lo_coup,
                            lo.id,
                            ])
        list1.append([
                        ob,
                        coup_list,
                        lo_ob,
                        ])
    for ob in qs2:
        coup_list = Coupling.objects.filter(parr_type=2, parrent=ob.id).order_by('name')
        list2.append([
                        ob,
                        coup_list,
                        ])

    return [list1, list2]

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def pw_add(request, kvar):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 2})

    if request.method == 'POST':
        form = add_PW_Form(request.POST)
        if form.is_valid():
            c_xy = coord_xy(form.cleaned_data['coord'].split(','))

            n_PW = PW_cont.objects.create(
                                        parrent_id=int(kvar),
                                        name=form.cleaned_data['name'],
                                        obj_type=int(form.cleaned_data['obj_type']),
                                        object_owner=form.cleaned_data['object_owner'],
                                        rasp=form.cleaned_data['rasp'],
                                        prim=form.cleaned_data['prim'],
                                        coord_x=c_xy[0],
                                        coord_y=c_xy[1],
                                        )
            to_his([request.user, 10, n_PW.id, 1, 0, 'name: '+n_PW.name])

            return HttpResponseRedirect('/cable/?kv='+str(kvar))
    else:
        form = add_PW_Form()

    return render(request, 'cable_new.html', {'form_pw': form,
                                              'kvar': kvar,
                                              })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def coup_add(request, kvar, p_t, p_id):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 4})

    if request.method == 'POST':
        form = add_Coup_Form(request.POST)
        if form.is_valid():
            c_xy = coord_xy(form.cleaned_data['coord'].split(','))

            n_coup = Coupling.objects.create(
                                            parrent=int(p_id),
                                            parr_type=int(p_t),
                                            name=form.cleaned_data['name'],
                                            name_type=form.cleaned_data['name_type'],
                                            installed=form.cleaned_data['installed'],
                                            object_owner=form.cleaned_data['object_owner'],
                                            date_ent=form.cleaned_data['date_ent'],
                                            rasp=form.cleaned_data['rasp'],
                                            prim=form.cleaned_data['prim'],
                                            coord_x=c_xy[0],
                                            coord_y=c_xy[1],
                                            )
            to_his([request.user, 8, n_coup.id, 1, 0, 'name: '+n_coup.name])

            return HttpResponseRedirect('/cable?kv='+str(kvar))
    else:
        form = add_Coup_Form()

    return render(request, 'cable_new.html', {'form_c': form,
                                              'kvar': kvar,
                                              })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def coup_view(request, s_coup):

    upd_visit(request.user, 'coup')
    try:
        coup = Coupling.objects.get(pk=s_coup)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'mess': 'объект не найден', 'back': 1})

    firms = firm.objects.filter(coup=True)
    p_all = Coupling_ports.objects.all()
    coup_p_list = p_all.filter(parrent_id=coup.id).order_by('cable_num','fiber_num')
    coup_clean = True if coup_p_list.count() == 0 else False
    parr1 = find_coup_parrent(coup)
    p_list = []
    n_mod = 1
    for ob in coup_p_list:
### new_module
        if ob.mod_num == n_mod:
            new_mod = False
        else:
            new_mod = True
            n_mod += 1
### new_cable
        cab_title = False
        if ob.fiber_num == 1:
            n_mod = 1
            rem_coup = p_all.get(pk=ob.up_id).parrent   #соседняя муфта
            parr2 = find_coup_parrent(rem_coup)
            info = ob.up_info.split('∿')
            if info[1] != '0':
                try:
                    info[0] = firms.get(pk=int(info[1])).name
                except:
                    info[0] = 'владелец не найден в справочнике фирм... '
            cab_title = {'cab':[ob.cable_num,
                                Templ_cable.objects.get(pk=ob.cable_type).name,
                                info,
                                conf.N_CAB_COLORS[ob.cable_num] if ob.cable_num < 15 else '#B5FFCE',
                                ],
                         'rem':[rem_coup,
                                parr2,
                                ],
                         }
### up
        fin = False
        hop = 1                 #колич.пройденных муфт
        fin_id = 0              #id конечного порта в муфте - для маркера
        obj_ty, obj_cr = [], []
        parr3 = []              #объект-родитель
        first_id = ob.up_id     #detect loopback
        start_id = ob.up_id
        owner_f = ob.up_info.split('∿')[0]

        while not fin:
            par1 = p_all.get(pk=start_id)
            if par1.int_c_status == 0:      #обрыв
                fin = True
                obj_ty = 0
                obj_cr = par1.parrent
                fin_id = par1.id
                parr3 = find_coup_parrent(obj_cr)
                continue
            elif par1.int_c_dest == 1:      #кросс
                fin = True
                obj_ty = 1
                try:
                    obj_cr = Cross_ports.objects.get(pk=par1.int_c_id)
                except ObjectDoesNotExist:
                    obj_ty = 8
                    obj_cr = 'link error'
                continue
            else:                           #варка кабель-кабель
                par2 = p_all.get(pk=par1.int_c_id)
                start_id = par2.up_id
                hop += 1
                if first_id == start_id:
                    fin = True
                    obj_ty = 8
                    obj_cr = 'loopback detected'
### repack
        if ob.int_c_status != 0 and ob.int_c_dest == 0:
            cr_int_port = coup_p_list.get(pk=ob.int_c_id)
            cab_num = cr_int_port.cable_num
            if cab_num > 14:
                cab_num = 14
            cr_cab_color = conf.N_CAB_COLORS[cab_num]
        else:
            cr_int_port = ''
            cr_cab_color = 'white'

        p_list.append({'f':[ob.id,
                            ob.fiber_num,
                            [ob.fiber_color, conf.RU_COLOR_LIST[ob.fiber_color] if ob.fiber_color in conf.RU_COLOR_LIST else ob.fiber_color],
                            cab_title,                 #3-new_cab
                            ob.mod_num,
                            [ob.mod_color, conf.RU_COLOR_LIST[ob.mod_color] if ob.mod_color in conf.RU_COLOR_LIST else ob.mod_color],
                            coup_p_list.filter(cable_num=ob.cable_num, mod_num=ob.mod_num).count() if (new_mod or ob.fiber_num == 1) else False, #6-new_mod
                            ob.changed,
                            ob.prim,
                            ob.p_valid,
                            owner_f,
                            ],
                       'cr':[ob.int_c_status,
                             ob.int_c_dest,
                             #coup_p_list.get(pk=ob.int_c_id) if ob.int_c_status != 0 and ob.int_c_dest == 0 else '',
                             cr_int_port,
                             Cross_ports.objects.get(pk=ob.int_c_id) if ob.int_c_status != 0 and ob.int_c_dest == 1 else '',
                             #conf.N_CAB_COLORS[coup_p_list.get(pk=ob.int_c_id).cable_num] if ob.int_c_status != 0 and ob.int_c_dest == 0 else 'white',
                             cr_cab_color,
                            ],
                       'up':[obj_ty,
                             obj_cr,
                             parr3,
                             fin_id,
                             hop,
                            ]
                       })

    if coup.parr_type == 0:
        try:
            kvar_id = Locker.objects.get(pk=coup.parrent).parrent.kvar
        except ObjectDoesNotExist:
            kvar_id = False
    elif coup.parr_type == 1:
        kvar_id = Building.objects.get(pk=coup.parrent).kvar
    elif coup.parr_type == 2:
        kvar_id = PW_cont.objects.get(pk=coup.parrent).parrent.id
    kvar = Kvartal.objects.get(pk=kvar_id) if kvar_id else False

    try:
        sel = int(request.GET['sel'])        #маркер
    except:
        sel = 0
    try:
        to_print = int(request.GET['to_print'])
    except:
        to_print = False

    return render(request, 'coup_view.html', {
                                            'kvar': kvar,
                                            'coup': coup,
                                            'coup_clean': coup_clean,
                                            'parr1': parr1,
                                            'p_list': p_list,
                                            'sel': sel,
                                            'to_print': to_print,
                                            })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_up(request, s_coup, cab_num):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})
    
    c_num = int(cab_num)
    n_num = c_num-1
    if c_num == 1:
        return HttpResponseRedirect('../')
    
    p_list = Coupling_ports.objects.filter(parrent_id=s_coup)
    
    if c_num <= 0 or p_list.filter(cable_num=0).exists():
        return render(request, 'error.html', {'mess': 'err870', 'back': 1})
    
    with transaction.atomic():
        
        p_list2 = p_list.filter(cable_num=n_num)
        if p_list2.count() != 0:
            p_list2.update(cable_num=0)
        
        p_list1 = p_list.filter(cable_num=c_num)
        if p_list1.count() != 0:
            p_list1.update(cable_num=n_num)
        else:
            return HttpResponseRedirect('../')
        
        p_list2 = p_list.filter(cable_num=0)
        if p_list2.count() != 0:
            p_list2.update(cable_num=c_num)
    
    vols_cab_up(s_coup, c_num)
    
    return HttpResponseRedirect('../')

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def chain(request, p_id, p_type):

    ch_list2 = chain_trace(p_id, p_type)

    if ch_list2:
        return render(request, 'chain.html', {'ch_list': ch_list2})
    else:
        return render(request, 'error.html', {'mess': 'ошибка трассировки', 'back': 2})

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_add1(request, s_coup, kvar):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    #source_coup = Coupling.objects.get(pk=s_coup)
    if request.method == 'POST':
        form = find_Form_kv(request.POST)
        if form.is_valid():
            kvar = form.cleaned_data['kvar']

    obj_list = create_obj_list(kvar)
    form = find_Form_kv(initial={'kvar': kvar})

    return render(request, 'coup_cab_add1.html', {
                                                'form': form,
                                                'kvar': kvar,
                                                'list1': obj_list[0],
                                                'list2': obj_list[1],
                                                })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_add2(request, s_coup, kvar, d_coup):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 2})

    s_c = Coupling.objects.get(pk=int(s_coup))
    d_c = Coupling.objects.get(pk=int(d_coup))

    if (s_coup == d_coup) and s_c.parr_type != 0:                   #experimental
        return HttpResponseRedirect('../')

    if request.method == 'POST':
        form = coup_link_Form(request.POST)
        if form.is_valid():
            sel_cable = Templ_cable.objects.get(pk=int(form.cleaned_data['sel_cable']))
            m_capa_list = sel_cable.mod_capa_list.split(',')
            m_col_list = sel_cable.mod_color_list.split(',')
            f_col_list = sel_cable.fiber_colors_list.split(',')

            phys_len = form.cleaned_data['phys_len']
            res_len = form.cleaned_data['res_len']
            date_ent = form.cleaned_data['date_ent']
            owner = form.cleaned_data['owner']
            
            cab_num1 = 1
            while Coupling_ports.objects.filter(parrent_id=s_c.id, cable_num=cab_num1).count() != 0:
                cab_num1 += 1
            cab_num2 = 1
            while (Coupling_ports.objects.filter(parrent_id=d_c.id, cable_num=cab_num2).count() != 0) or ((s_coup == d_coup) and (cab_num1 == cab_num2)):     #experimental
                cab_num2 += 1
            
            with transaction.atomic():
                i = 0
                while i < sel_cable.capacity:
                    i = i + 1
                    m_num = int(m_capa_list[i-1].split('-')[1])
                    m_col = m_col_list[m_num-1]
                    
                    s_c_p = Coupling_ports.objects.create(
                                                        parrent_id=s_c.id,
                                                        cable_num=cab_num1,
                                                        cable_type=sel_cable.id,
                                                        fiber_num=i,
                                                        fiber_color=f_col_list[i-1],
                                                        mod_num=m_num,
                                                        mod_color=m_col
                                                        )
                    d_c_p = Coupling_ports.objects.create(
                                                        parrent_id=d_c.id,
                                                        cable_num=cab_num2,
                                                        cable_type=sel_cable.id,
                                                        fiber_num=i,
                                                        fiber_color=f_col_list[i-1],
                                                        mod_num=m_num,
                                                        mod_color=m_col
                                                        )
                    s_c_p.up_id = d_c_p.id
                    d_c_p.up_id = s_c_p.id
                    
                    if i == 1:
                        s_c_p.up_info = '∿'+str(owner)+'∿'+str(phys_len)+'∿'+res_len+'∿'+str(date_ent)
                        d_c_p.up_info = '∿'+str(owner)+'∿'+str(phys_len)+'∿'+res_len+'∿'+str(date_ent)
                    
                    s_c_p.save()
                    d_c_p.save()
            
            to_his([request.user, 8, s_c.id, 12, 0, 'from: '+str(s_c.name)+' cab_num: '+str(cab_num1)+'; to: '+str(d_c.name)+' cab_num: '+str(cab_num2)+'; cab: '+sel_cable.name])
            to_his([request.user, 8, d_c.id, 12, 0, 'from: '+str(s_c.name)+' cab_num: '+str(cab_num1)+'; to: '+str(d_c.name)+' cab_num: '+str(cab_num2)+'; cab: '+sel_cable.name])

            return HttpResponseRedirect('../../')

    else:
        #form = coup_link_Form(initial={'date_ent': datetime.date.today()})
        form = coup_link_Form()

    return render(request, 'coup_cab_add2.html', {
                                                    'form': form,
                                                    's_coup': s_c,
                                                    'd_coup': d_c,
                                                    })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def int_c(request, s_coup, s_port, stat, multi, dest_type=None):
    
    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 3})
    
    coup = Coupling.objects.get(pk=s_coup)
    s_p = Coupling_ports.objects.get(pk=s_port)
    
    if request.method == 'POST':
        try:
            if dest_type == '0':
                d_port = int(request.POST['f_port'])
                d_p = Coupling_ports.objects.get(pk=d_port)
            else:
                d_port = int(request.POST['cr_port'])
                d_p = Cross_ports.objects.get(pk=d_port)
        except:
            return HttpResponseRedirect('../')
        
        if dest_type == '0':
            if s_p.int_c_status != 0 or d_p.int_c_status != 0:      #проверка портов перед записью
                return HttpResponseRedirect('../err304')
            if str(s_port) == str(d_port):
                return HttpResponseRedirect('../')
            with transaction.atomic():
                s_p.int_c_id = d_port
                d_p.int_c_id = s_port
                s_p.int_c_status = int(stat)
                d_p.int_c_status = int(stat)
                s_p.int_c_dest = 0
                d_p.int_c_dest = 0
                s_p.changed = False
                d_p.changed = False
                s_p.save()
                d_p.save()
            
            if s_p.cable_num != d_p.cable_num: #разные кабели -> попытаться скроссировать остальные стекла
                if Coupling_ports.objects.filter(parrent_id=s_p.parrent_id, cable_num=s_p.cable_num, fiber_num=(s_p.fiber_num+1)).exists():
                    if Coupling_ports.objects.filter(parrent_id=d_p.parrent_id, cable_num=d_p.cable_num, fiber_num=(d_p.fiber_num+1)).exists():
                        if multi == '1':
                            e_p = int(request.POST['end_p0'])
                            int_c_multi(s_p, d_p, int(stat), e_p)
        
        if dest_type == '1':
            if s_p.int_c_status != 0 or d_p.cab_p_id != 0:          #проверка портов перед записью
                return HttpResponseRedirect('../err305')
            with transaction.atomic():
                s_p.int_c_id = d_port
                d_p.cab_p_id = s_port
                s_p.int_c_status = 2
                s_p.int_c_dest = 1
                s_p.changed = False
                s_p.save()
                d_p.save()
            # multi
            if Coupling_ports.objects.filter(parrent_id=s_p.parrent_id, cable_num=s_p.cable_num, fiber_num=(s_p.fiber_num+1)).exists():
                if Cross_ports.objects.filter(parrent_id=d_p.parrent_id, num=(d_p.num+1)).exists():
                    if multi == '1':
                        e_p = int(request.POST['end_p1'])
                        int_c_multi_cross(s_p, d_p, e_p)
        
        to_his([request.user, 9, s_p.id, 4, 0, 'муфта: '+coup.name+'; from: id-'+str(s_p.id)+' to: id-'+str(d_p.id)+'; dest_type: '+dest_type+'; multi:'+multi])
        to_his([request.user, 9, d_p.id, 4, 0, 'муфта: '+coup.name+'; from: id-'+str(d_p.id)+' to: id-'+str(s_p.id)+'; dest_type: '+dest_type+'; multi:'+multi])
        
        return HttpResponseRedirect('../../../../')
    
    curr_cab = 0
    cab_list = []
    p_list = []
    coup_p_list = Coupling_ports.objects.filter(parrent_id=coup.id).order_by('cable_num', 'fiber_num')
    if int(stat) == 1:                 #транзит -> кабель должен быть одного типа и с разными номерами в муфте
        coup_p_list = coup_p_list.filter(cable_type=s_p.cable_type).exclude(cable_num=s_p.cable_num)
    for ob in coup_p_list:
        if curr_cab != ob.cable_num:
            curr_cab = ob.cable_num
            cab_list.append([
                            curr_cab,
                            Coupling_ports.objects.get(pk=ob.up_id),
                            ])
            p_list.append(coup_p_list.filter(cable_num=curr_cab))
            #print(p_list[0].count())
    cr_list = []
    cr_p_list = []
    if coup.parr_type == 0 and int(stat) != 1:
        cr_list = Cross.objects.filter(parrent_id=coup.parrent).order_by('name')
        for ob in cr_list:
            cr_p_list.append(Cross_ports.objects.filter(parrent_id=ob.id).order_by('num'))
            
    e_p = Coupling_ports.objects.filter(parrent_id=s_p.parrent_id,cable_num=s_p.cable_num).count() #end_port
    
    return render(request, 'coup_int_c.html', {
                                            's_p': s_p,
                                            'e_p': [e_p, multi],
                                            'cab_list': cab_list,
                                            'p_list': p_list,
                                            'cr_list': cr_list,
                                            'cr_p_list': cr_p_list,
                                            })


def int_c_multi(s_p, d_p, stat, e_p):

    s_p_list = Coupling_ports.objects.filter(
                                            parrent_id=s_p.parrent_id,
                                            cable_num=s_p.cable_num,
                                            fiber_num__gt=s_p.fiber_num,
                                            fiber_num__lte=e_p
                                            )
    d_p_list = Coupling_ports.objects.filter(parrent_id=d_p.parrent_id,cable_num=d_p.cable_num,fiber_num__gt=d_p.fiber_num)
    count_op = s_p_list.count() if (s_p_list.count() < d_p_list.count()) else d_p_list.count()
    i = 0
    while i < count_op:
        i += 1
        #s_p_m = Coupling_ports.objects.get(parrent_id=s_p.parrent_id,cable_num=s_p.cable_num,fiber_num=(s_p.fiber_num+i))
        s_p_m = s_p_list.get(parrent_id=s_p.parrent_id, cable_num=s_p.cable_num, fiber_num=(s_p.fiber_num+i))
        #d_p_m = Coupling_ports.objects.get(parrent_id=d_p.parrent_id,cable_num=d_p.cable_num,fiber_num=(d_p.fiber_num+i))
        d_p_m = d_p_list.get(parrent_id=d_p.parrent_id, cable_num=d_p.cable_num, fiber_num=(d_p.fiber_num+i))
        if s_p_m.int_c_status == 0 and d_p_m.int_c_status == 0:
            with transaction.atomic():
                s_p_m.int_c_id = d_p_m.id
                d_p_m.int_c_id = s_p_m.id
                s_p_m.int_c_status = stat
                d_p_m.int_c_status = stat
                s_p_m.int_c_dest = 0
                d_p_m.int_c_dest = 0
                s_p_m.changed = False
                d_p_m.changed = False
                s_p_m.save()
                d_p_m.save()

    return i

def int_c_multi_cross(s_p, d_p, e_p):

    s_p_list = Coupling_ports.objects.filter(
                                            parrent_id=s_p.parrent_id,
                                            cable_num=s_p.cable_num,
                                            fiber_num__gt=s_p.fiber_num,
                                            fiber_num__lte=e_p
                                            )
    d_p_list = Cross_ports.objects.filter(parrent_id=d_p.parrent_id, num__gt=d_p.num)
    count_op = s_p_list.count() if (s_p_list.count() < d_p_list.count()) else d_p_list.count()
    i = 0
    while i < count_op:
        i += 1
        #s_p_m = Coupling_ports.objects.get(parrent_id=s_p.parrent_id, cable_num=s_p.cable_num, fiber_num=(s_p.fiber_num+i))
        s_p_m = s_p_list.get(parrent_id=s_p.parrent_id,cable_num=s_p.cable_num,fiber_num=(s_p.fiber_num+i))
        #d_p_m = Cross_ports.objects.get(parrent_id=d_p.parrent_id, num=(d_p.num+i))
        d_p_m = d_p_list.get(parrent_id=d_p.parrent_id,num=(d_p.num+i))
        if s_p_m.int_c_status == 0 and d_p_m.cab_p_id == 0:
            with transaction.atomic():
                s_p_m.int_c_id = d_p_m.id
                d_p_m.cab_p_id = s_p_m.id
                s_p_m.int_c_status = 2
                s_p_m.int_c_dest = 1
                s_p_m.changed = False
                s_p_m.save()
                d_p_m.save()

    return i

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def int_del(request, s_coup, s_port):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    s_p = Coupling_ports.objects.get(pk=s_port)
    if s_p.int_c_status == 0:
        return render(request, 'error.html', {'mess': 'err307', 'back': 1})
    if s_p.int_c_dest == 0:
        d_p = Coupling_ports.objects.get(pk=s_p.int_c_id)
        if d_p.int_c_status == 0:
            return render(request, 'error.html', {'mess': 'err308', 'back': 1})
    elif s_p.int_c_dest == 1:
        d_p = Cross_ports.objects.get(pk=s_p.int_c_id)
        if d_p.cab_p_id == 0:
            return render(request, 'error.html', {'mess': 'err309', 'back': 1})

    if request.method == 'POST':
        with transaction.atomic():
            if s_p.int_c_dest == 0:
                d_p.int_c_dest = 0
                d_p.int_c_id = 0
                d_p.int_c_status = 0
            elif s_p.int_c_dest == 1:
                d_p.cab_p_id = 0
            s_p.int_c_dest = 0
            s_p.int_c_id = 0
            s_p.int_c_status = 0
            s_p.save()
            d_p.save()

        to_his([request.user, 9, s_p.id, 7, 0, 'муфта: '+s_p.parrent.name+'; from: id-'+str(s_p.id)+' to: id-'+str(d_p.id)])
        to_his([request.user, 9, d_p.id, 7, 0, 'муфта: '+d_p.parrent.name+'; from: id-'+str(d_p.id)+' to: id-'+str(s_p.id)])

        return HttpResponseRedirect('../')

    return render(request, 'coup_int_del.html', {'s_p': s_p, 'd_p': d_p})

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def int_edit(request, s_coup, p_id):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    s_p = Coupling_ports.objects.get(pk=p_id)
    if request.method == 'POST':
        form = coup_p_edit_Form(request.POST)
        if form.is_valid():
            change = False
            if form.cleaned_data['valid'] != s_p.p_valid:
                change = True
                s_p.p_valid = form.cleaned_data['valid']
            if s_p.int_c_status != 0 and s_p.int_c_dest == 0 and form.cleaned_data['int_c_status'] != s_p.int_c_status:
                change = True
                s_p.int_c_status = form.cleaned_data['int_c_status']
                d_p = Coupling_ports.objects.get(parrent=s_p.parrent, int_c_id=s_p.id)
                d_p.int_c_status = form.cleaned_data['int_c_status']
                d_p.save()
            if form.cleaned_data['changed'] != s_p.changed:
                change = True
                s_p.changed = form.cleaned_data['changed']
            if form.cleaned_data['prim'] != s_p.prim:
                change = True
                s_p.prim = form.cleaned_data['prim']
            
            s_info_1 = s_p.up_info.split('∿')
            s_info_2 = str(form.cleaned_data['owner'])
            if s_info_2 != s_info_1[0]:
                change = True
                d_p = Coupling_ports.objects.get(pk=s_p.up_id)
                d_info_1 = d_p.up_info.split('∿')
                s_info_1[0] = s_info_2
                d_info_1[0] = s_info_2
                s_p.up_info = '∿'.join(s_info_1)
                d_p.up_info = '∿'.join(d_info_1)
                #s_p.save()
                d_p.save()

            if change:
                s_p.save()
                to_his([request.user, 9, s_p.id, 2, 0, 'муфта: '+s_p.parrent.name+'; cab: '+str(s_p.cable_num)+'; fiber: '+str(s_p.fiber_num)])

            return HttpResponseRedirect('../')

    form = coup_p_edit_Form(initial={
                                    'valid': s_p.p_valid,
                                    'int_c_status': s_p.int_c_status,
                                    'changed': s_p.changed,
                                    'prim': s_p.prim,
                                    'owner': s_p.up_info.split('∿')[0],
                                    })

    return render(request, 'coup_int_edit.html', {'form': form, 's_p': s_p})

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_edit(request, s_coup, p_id):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    s_p = Coupling_ports.objects.get(pk=p_id)
    d_p = Coupling_ports.objects.get(pk=s_p.up_id)
    s_info = s_p.up_info.split('∿')[:5]
    d_info = d_p.up_info.split('∿')[:5]
    
    if len(s_info) < 5:
        s_info = ['','0','0','0',None]
    if len(d_info) < 5:
        d_info = ['','0','0','0',None]
    
    if request.method == 'POST':
        form = coup_cab_edit_Form(request.POST)
        if form.is_valid():
            owner = str(form.cleaned_data['owner'])
            s_info[1] = owner
            s_info[2] = str(form.cleaned_data['phys_len'])
            s_info[3] = str(form.cleaned_data['res_len'])
            s_info[4] = str(form.cleaned_data['date_ent'])
            d_info[1] = owner
            d_info[2] = str(form.cleaned_data['phys_len'])

            with transaction.atomic():
                s_p.up_info = '∿'.join(s_info)
                d_p.up_info = '∿'.join(d_info)
                s_p.save()
                d_p.save()
            
            if form.cleaned_data['owner_f']:
                owner_f = owner if (owner != '0') else ''
                sd_p_list = Coupling_ports.objects.filter(Q (parrent_id=s_p.parrent_id, cable_num=s_p.cable_num) |
                                                          Q (parrent_id=d_p.parrent_id, cable_num=d_p.cable_num) ).order_by('id')
                #print(sd_p_list.values_list('id', flat=True).count())
                with transaction.atomic():
                    for ob in sd_p_list:
                        if ob.fiber_num == 1:
                            info = ob.up_info.split('∿')
                            info[0] = owner_f
                            ob.up_info = '∿'.join(info)
                        else:
                            ob.up_info = owner_f
                        
                        ob.save()
                    
            to_his([request.user, 9, s_p.id, 2, 0, 'м: '+s_p.parrent.name+'; cab: '+str(s_p.cable_num)+' INFO'])

            return HttpResponseRedirect('../')

    form = coup_cab_edit_Form(initial={'owner': s_info[1],
                                       'phys_len': s_info[2],
                                       'res_len': s_info[3],
                                       'date_ent': s_info[4],
                                       })
    
    return render(request, 'coup_cab_edit.html', {'form': form,
                                                  's_p': s_p,
                                                  'd_p': d_p,
                                                  })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_del(request, s_coup, cab):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    coup = Coupling.objects.get(pk=s_coup)
    del_p_list1 = Coupling_ports.objects.filter(parrent_id=coup.id, cable_num=int(cab)).order_by('fiber_num')
    rem_p_id = del_p_list1.first().up_id
    rem_p = Coupling_ports.objects.get(pk=rem_p_id)
    del_p_list2 = Coupling_ports.objects.filter(parrent_id=rem_p.parrent.id, cable_num=rem_p.cable_num).order_by('fiber_num')
    del_ok1 = False if del_p_list1.filter(int_c_status__gt=0).exists() else True
    del_ok2 = False if del_p_list2.filter(int_c_status__gt=0).exists() else True

    if request.method == 'POST' and del_ok1 and del_ok2:

        with transaction.atomic():
            del_p_list1.delete()
            del_p_list2.delete()

        to_his([request.user, 8, coup.id, 13, 0, 'from: '+coup.name+' to: '+rem_p.parrent.name+'; cab_num: '+cab])
        to_his([request.user, 8, rem_p.parrent.id, 13, 0, 'from: '+coup.name+' to: '+rem_p.parrent.name+'; cab_num: '+cab])

        vols_cab_remove(s_coup, cab)

        return HttpResponseRedirect('../')

    return render(request, 'coup_cab_del.html', {'coup': coup,
                                                 'cab': cab,
                                                 'rem_p': rem_p,
                                                 'del_ok1': del_ok1,
                                                 'del_ok2': del_ok2,
                                                 })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_move1(request, s_coup, kvar, cab):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 2})

    source_coup = Coupling.objects.get(pk=s_coup)
    del_p_list1 = Coupling_ports.objects.filter(parrent_id=source_coup.id, cable_num=int(cab)).order_by('fiber_num')
    del_ok1 = False if del_p_list1.filter(int_c_status__gt=0).exists() else True

    if request.method == 'POST':
        form = find_Form_kv(request.POST)
        if form.is_valid():
            kvar = form.cleaned_data['kvar']

    obj_list = create_obj_list(kvar)

    form = find_Form_kv(initial={'kvar': kvar})

    return render(request, 'coup_cab_move1.html', {'form': form,
                                                   'kvar': kvar,
                                                   'coup': source_coup,
                                                   'del_ok1': del_ok1,
                                                   'list1': obj_list[0],
                                                   'list2': obj_list[1],
                                                   })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def cab_move2(request, s_coup, kvar, cab, d_coup):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 3})

    if s_coup == d_coup:
        return HttpResponseRedirect('../')

    coup1 = Coupling.objects.get(pk=s_coup)                 #1 муфта
    coup3 = Coupling.objects.get(pk=d_coup)                 #3 муфта

    p_list1 = Coupling_ports.objects.filter(parrent_id=coup1.id, cable_num=int(cab)).order_by('fiber_num')

    p1_c2 = Coupling_ports.objects.get(pk=p_list1.first().up_id)
    coup2 = Coupling.objects.get(pk=p1_c2.parrent_id)       #2 муфта
    p_list2 = Coupling_ports.objects.filter(parrent_id=coup2.id, cable_num=p1_c2.cable_num).order_by('fiber_num')
    if coup2 == coup3:
        return HttpResponseRedirect('../')                  #петля
    del_ok = False if p_list1.filter(int_c_status__gt=0).exists() else True
    capa = p_list1.count()

    cab_num3 = 1                                            #ищем свободный номер кабеля в 3 муфте
    while Coupling_ports.objects.filter(parrent_id=coup3.id, cable_num=cab_num3).count() != 0:
        cab_num3 += 1

    if not del_ok:
        return render(request, 'error.html', {'mess': 'err311', 'back': 3})
    else:
        with transaction.atomic():
            i = 0
            while i < capa:
                i = i + 1
                s_p = p_list1.get(fiber_num=i)
                c_p = p_list2.get(fiber_num=i)
                d_p = Coupling_ports.objects.create(parrent_id=coup3.id,
                                                    cable_num=cab_num3,
                                                    cable_type=s_p.cable_type,
                                                    fiber_num=i,
                                                    fiber_color=s_p.fiber_color,
                                                    mod_num=s_p.mod_num,
                                                    mod_color=s_p.mod_color,
                                                    up_id=c_p.id,
                                                    up_info=s_p.up_info
                                                    )
                c_p.up_id = d_p.id
                c_p.save()
                d_p.save()

            p_list1.delete()

    to_his([request.user, 8, coup1.id, 14, 0, 'from: '+coup1.name+' to: '+coup3.name+' cab_num: '+str(cab_num3)+'; change: '+coup2.name+' cab_num: '+str(p1_c2.cable_num)])
    to_his([request.user, 8, coup3.id, 14, 0, 'from: '+coup1.name+' to: '+coup3.name+' cab_num: '+str(cab_num3)+'; change: '+coup2.name+' cab_num: '+str(p1_c2.cable_num)])

    vols_cab_remove(s_coup, cab)

    return HttpResponseRedirect('../../../')

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def pw_edit(request, kvar, s_pw):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 2})

    pw = PW_cont.objects.get(pk=s_pw)
    if request.method == 'POST':
        form = add_PW_Form(request.POST)
        if form.is_valid():
            change = False

            if form.cleaned_data['name'] != pw.name:
                change = True
                pw.name = form.cleaned_data['name']
            if form.cleaned_data['obj_type'] != pw.obj_type:
                change = True
                pw.obj_type = form.cleaned_data['obj_type']
            if form.cleaned_data['object_owner'] != pw.object_owner:
                change = True
                pw.object_owner = form.cleaned_data['object_owner']
            if form.cleaned_data['rasp'] != pw.rasp:
                change = True
                pw.rasp = form.cleaned_data['rasp']
            if form.cleaned_data['prim'] != pw.prim:
                change = True
                pw.prim = form.cleaned_data['prim']

            if form.cleaned_data['coord'] != str(round(pw.coord_x))+','+str(round(pw.coord_y)):
                change = True
                xy2 = coord_xy(form.cleaned_data['coord'].split(','))
                pw.coord_x = xy2[0]
                #pw.coord_x = int(round(float(c_xy[0])))
                pw.coord_y = xy2[1]
                #pw.coord_y = int(round(float(c_xy[1])))

            if change:
                pw.save()
                to_his([request.user, 10, pw.id, 2, 0, 'name: '+pw.name])

            return HttpResponseRedirect('/cable/?kv='+str(kvar))

    else:
        form = add_PW_Form(initial={'name': pw.name,
                                    'obj_type': pw.obj_type,
                                    'object_owner': pw.object_owner,
                                    #'object_owner_list': pw.object_owner,
                                    'rasp': pw.rasp, 'prim': pw.prim,
                                    'coord': str(round(pw.coord_x))+','+str(round(pw.coord_y))
                                    })

    return render(request, 'cable_new.html', {'kvar': kvar,
                                              'pw': pw,
                                              'form_pw': form,
                                              })

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def pw_del(request, kvar, s_pw):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 2})

    pw = PW_cont.objects.get(pk=s_pw)
    del_ok = False if Coupling.objects.filter(parrent=pw.id, parr_type=2).count() != 0 else True

    if request.method == 'POST' and del_ok:

        to_his([request.user, 10, pw.id, 13, 0, 'name: '+pw.name])
        pw.delete()

        return HttpResponseRedirect('/cable/?kv='+str(kvar))

    return render(request, 'cable_del.html', {'pw': pw, 'del_ok': del_ok})

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def coup_edit(request, s_coup):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    move_pos = False
    coup = Coupling.objects.get(pk=s_coup)
    if request.method == 'POST':
        form = add_Coup_Form(request.POST)
        if form.is_valid():
            change = False

            if form.cleaned_data['name'] != coup.name:
                change = True
                coup.name = form.cleaned_data['name']
            if form.cleaned_data['name_type'] != coup.name_type:
                change = True
                coup.name_type = form.cleaned_data['name_type']
            if form.cleaned_data['object_owner'] != coup.object_owner:
                change = True
                coup.object_owner = form.cleaned_data['object_owner']
            if form.cleaned_data['installed'] != coup.installed:
                change = True
                coup.installed = form.cleaned_data['installed']
            if form.cleaned_data['date_ent'] != coup.date_ent:
                change = True
                coup.date_ent = form.cleaned_data['date_ent']
            if form.cleaned_data['rasp'] != coup.rasp:
                change = True
                coup.rasp = form.cleaned_data['rasp']
            if form.cleaned_data['prim'] != coup.prim:
                change = True
                coup.prim = form.cleaned_data['prim']

            #xy1 = [int(round(coup.coord_x)), int(round(coup.coord_y))]
            #if form.cleaned_data['coord'] != str(xy1[0])+','+str(xy1[1]):
            if form.cleaned_data['coord'] != str(round(coup.coord_x))+','+str(round(coup.coord_y)):
                change = True
                xy1 = coord_xy([coup.coord_x, coup.coord_y])
                xy2 = coord_xy(form.cleaned_data['coord'].split(','))
                #xy2 = [int(round(float(c_xy[0]))), int(round(float(c_xy[1])))]
                #move_pos = [xy1, xy2]
                move_pos = [str(xy1[0])+','+str(xy1[1]), str(xy2[0])+','+str(xy2[1])]
                coup.coord_x = xy2[0]
                coup.coord_y = xy2[1]
                try:
                    if coup.parr_type == 0:
                        lo = Locker.objects.get(pk=coup.parrent)
                        lo.coord_x = xy2[0]
                        lo.coord_y = xy2[1]
                        lo.save()
                except:
                    pass

            if change:
                coup.save()
                to_his([request.user, 8, coup.id, 2, 0, 'name: '+coup.name])
            if move_pos:
                vols_coup_move(coup.id, move_pos)

            return HttpResponseRedirect('../')

    else:
        form = add_Coup_Form(initial={'name': coup.name,
                                      'name_type': coup.name_type,
                                      'object_owner': coup.object_owner,
                                      #'object_owner_list': coup.object_owner,
                                      'installed': coup.installed,
                                      'date_ent': coup.date_ent,
                                      'rasp': coup.rasp,
                                      'prim': coup.prim,
                                      'coord': str(round(coup.coord_x))+','+str(round(coup.coord_y))
                                      })

    return render(request, 'cable_new.html', {'coup': coup, 'form_c': form})

#___________________________________________________________________________


@login_required(login_url='/core/login/')
def coup_del(request, s_coup):

    if not request.user.has_perm("core.can_cable_edit"):
        return render(request, 'denied.html', {'mess': 'недостаточно прав', 'back': 1})

    coup = Coupling.objects.get(pk=s_coup)
    del_ok1 = False if Coupling_ports.objects.filter(parrent_id=coup.id).count() != 0 else True
    ## сделать - удалять муфты без УД ###################################################
    del_ok2 = False if coup.parr_type == 0 else True ####################################

    if request.method == 'POST' and del_ok1 and del_ok2:
        to_his([request.user, 8, coup.id, 13, 0, 'name: '+coup.name])
        coup.delete()

        return HttpResponseRedirect('../../')

    return render(request, 'coup_del.html', {
                                            'coup': coup,
                                            'del_ok1': del_ok1,
                                            'del_ok2': del_ok2,
                                            })

#___________________________________________________________________________


def coord_xy(coord_t):
    try:
        #c_x = float(coord_t[0])
        c_x = int(round(float(coord_t[0])))
        #c_y = float(coord_t[1])
        c_y = int(round(float(coord_t[1])))
    except:
        c_x = 30
        c_y = 30
    return [c_x, c_y]

#___________________________________________________________________________
